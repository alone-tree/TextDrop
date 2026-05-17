# Copyright (C) 2026  alone-tree
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

import multiprocessing
import sys
import threading
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .config import AppConfig, load_config, save_config
from .constants import AUTO_ENTER_OPTIONS, DEFAULT_PORT
from .i18n import LANGUAGE_OPTIONS, tr
from .network import AddressCandidate, choose_address, find_available_port, list_address_candidates
from .paste import paste_text
from .qr import make_qr_png
from .server import LocalServer, ServerState
from .tokens import generate_token


APP_USER_MODEL_ID = "TextDrop.TextDrop.v0.1"


def _asset_path(name: str) -> str:
    base_dir = getattr(sys, "_MEIPASS", None)
    if base_dir:
        return str(Path(base_dir) / "assets" / name)
    return str(Path(__file__).resolve().parents[2] / "assets" / name)


def _set_windows_app_id() -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
    except Exception:
        pass


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self._lock = threading.RLock()
        self.config: AppConfig = load_config()
        self.candidates = list_address_candidates()
        self.selected_address = choose_address(self.candidates, self.config.selected_address)
        self.port = find_available_port(DEFAULT_PORT)
        self.server = LocalServer(
            self.port,
            ServerState(
                get_token=self._get_token,
                get_language=self._get_language,
                get_auto_enter=self._get_auto_enter,
                paste_text=paste_text,
            ),
        )

        self.status_value = QLabel()
        self.language_combo = QComboBox()
        self.auto_enter_combo = QComboBox()
        self.address_combo = QComboBox()
        self.url_edit = QLineEdit()
        self.qr_label = QLabel()
        self.token_value = QLabel()
        self.copy_button = QPushButton()
        self.refresh_token_button = QPushButton()
        self.exit_button = QPushButton()

        self._build_ui()
        self._connect_events()
        self.server.start()
        self._save_selected_address()
        self._apply_language()
        self._refresh_address_view()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.status_value.setText(tr(self.config.language, "status_closed"))
        self.server.stop()
        event.accept()

    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        title = QLabel("TextDrop")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        root.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        root.addLayout(form)

        self.status_label = QLabel()
        self.language_label = QLabel()
        self.auto_enter_label = QLabel()
        self.address_choice_label = QLabel()
        self.access_url_label = QLabel()
        self.token_label = QLabel()

        form.addRow(self.status_label, self.status_value)
        form.addRow(self.language_label, self.language_combo)
        form.addRow(self.auto_enter_label, self.auto_enter_combo)
        form.addRow(self.address_choice_label, self.address_combo)

        self.url_edit.setReadOnly(True)
        form.addRow(self.access_url_label, self.url_edit)
        form.addRow(self.token_label, self.token_value)

        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setMinimumSize(240, 240)
        root.addWidget(self.qr_label)

        buttons = QHBoxLayout()
        buttons.addStretch(1)
        buttons.addWidget(self.copy_button)
        buttons.addWidget(self.refresh_token_button)
        buttons.addWidget(self.exit_button)
        root.addLayout(buttons)

        self._fill_language_combo()
        self._fill_auto_enter_combo()
        self._fill_address_combo()
        self.setCentralWidget(central)
        self.resize(560, 620)

    def _connect_events(self) -> None:
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        self.auto_enter_combo.currentIndexChanged.connect(self._on_auto_enter_changed)
        self.address_combo.currentIndexChanged.connect(self._on_address_changed)
        self.copy_button.clicked.connect(self._copy_address)
        self.refresh_token_button.clicked.connect(self._confirm_refresh_token)
        self.exit_button.clicked.connect(self.close)

    def _fill_language_combo(self) -> None:
        self.language_combo.blockSignals(True)
        self.language_combo.clear()
        for code, label in LANGUAGE_OPTIONS:
            self.language_combo.addItem(label, code)
        index = self.language_combo.findData(self.config.language)
        self.language_combo.setCurrentIndex(max(index, 0))
        self.language_combo.blockSignals(False)

    def _fill_auto_enter_combo(self) -> None:
        self.auto_enter_combo.blockSignals(True)
        self.auto_enter_combo.clear()
        language = self.config.language
        for value, i18n_key in AUTO_ENTER_OPTIONS:
            self.auto_enter_combo.addItem(tr(language, i18n_key), value)
        index = self.auto_enter_combo.findData(self.config.auto_enter)
        self.auto_enter_combo.setCurrentIndex(max(index, 0))
        self.auto_enter_combo.blockSignals(False)

    def _fill_address_combo(self) -> None:
        self.address_combo.blockSignals(True)
        self.address_combo.clear()
        if self.candidates:
            for candidate in self.candidates:
                self.address_combo.addItem(candidate.label, candidate.address)
        else:
            self.address_combo.addItem(self.selected_address, self.selected_address)
        index = self.address_combo.findData(self.selected_address)
        self.address_combo.setCurrentIndex(max(index, 0))
        self.address_combo.blockSignals(False)

    def _apply_language(self) -> None:
        language = self.config.language
        self.setWindowTitle(tr(language, "window_title"))
        self.setWindowIcon(QIcon(_asset_path("app_icon.ico")))
        self.status_label.setText(f"{tr(language, 'status_label')}:")
        self.language_label.setText(f"{tr(language, 'language_label')}:")
        self.address_choice_label.setText(f"{tr(language, 'address_choice_label')}:")
        self.access_url_label.setText(f"{tr(language, 'access_url_label')}:")
        self.token_label.setText(f"{tr(language, 'token_label')}:")
        self.auto_enter_label.setText(f"{tr(language, 'auto_enter_label')}:")
        self.status_value.setText(tr(language, "status_running"))
        self.token_value.setText(tr(language, "token_enabled"))
        self.copy_button.setText(tr(language, "copy_address"))
        self.refresh_token_button.setText(tr(language, "refresh_token"))
        self.exit_button.setText(tr(language, "exit"))

    def _access_url(self) -> str:
        return f"http://{self.selected_address}:{self.port}/?token={self.config.token}"

    def _refresh_address_view(self) -> None:
        url = self._access_url()
        self.url_edit.setText(url)
        pixmap = QPixmap()
        pixmap.loadFromData(make_qr_png(url), "PNG")
        self.qr_label.setPixmap(
            pixmap.scaled(240, 240, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        )

    def _on_language_changed(self) -> None:
        language = self.language_combo.currentData()
        if not language:
            return
        with self._lock:
            self.config.language = language
            save_config(self.config)
        self._apply_language()
        self._fill_auto_enter_combo()

    def _on_auto_enter_changed(self) -> None:
        auto_enter = self.auto_enter_combo.currentData()
        if auto_enter is None:
            return
        with self._lock:
            self.config.auto_enter = auto_enter
            save_config(self.config)

    def _on_address_changed(self) -> None:
        address = self.address_combo.currentData()
        if not address:
            return
        self.selected_address = address
        self._save_selected_address()
        self._refresh_address_view()

    def _copy_address(self) -> None:
        QApplication.clipboard().setText(self._access_url())

    def _confirm_refresh_token(self) -> None:
        language = self.config.language
        result = QMessageBox.question(
            self,
            tr(language, "confirm_refresh_title"),
            tr(language, "confirm_refresh_message"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if result != QMessageBox.StandardButton.Yes:
            return
        with self._lock:
            self.config.token = generate_token()
            save_config(self.config)
        self._refresh_address_view()

    def _save_selected_address(self) -> None:
        with self._lock:
            self.config.selected_address = self.selected_address
            save_config(self.config)

    def _get_token(self) -> str:
        with self._lock:
            return self.config.token

    def _get_language(self) -> str:
        with self._lock:
            return self.config.language

    def _get_auto_enter(self) -> str:
        with self._lock:
            return self.config.auto_enter


def run_gui() -> int:
    multiprocessing.freeze_support()
    _set_windows_app_id()
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(_asset_path("app_icon.ico")))
    window = MainWindow()
    window.show()
    return app.exec()
