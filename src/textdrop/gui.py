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
import time
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
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
from .tls import ensure_tls_certificate
from .tokens import generate_token


APP_USER_MODEL_ID = "TextDrop.TextDrop.v0.1.2"
NETWORK_CHECK_INTERVAL_MS = 3000
CLIENT_CONNECTED_TTL_SECONDS = 12


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
        self._last_client_seen: float | None = None
        self.config: AppConfig = load_config()
        self.candidates = list_address_candidates()
        self.selected_address = choose_address(self.candidates, self.config.selected_address)
        self.port = find_available_port(DEFAULT_PORT)
        self.tls_paths, _ = ensure_tls_certificate(self._tls_hosts())
        self.server_state = ServerState(
            get_token=self._get_token,
            get_language=self._get_language,
            get_auto_enter=self._get_auto_enter,
            paste_text=paste_text,
            mark_client_connected=self._mark_client_connected,
        )
        self.server = self._create_server()

        self.status_value = QLabel()
        self.notice_label = QLabel()
        self.language_combo = QComboBox()
        self.auto_enter_combo = QComboBox()
        self.address_combo = QComboBox()
        self.use_https_checkbox = QCheckBox()
        self.use_https_label = QLabel()
        self.security_tip_label = QLabel()
        self.url_edit = QLineEdit()
        self.qr_label = QLabel()
        self.token_value = QLabel()
        self.copy_button = QPushButton()
        self.refresh_token_button = QPushButton()
        self.exit_button = QPushButton()

        self._build_ui()
        self._connect_events()
        self.server.start()
        self.network_timer = QTimer(self)
        self.network_timer.setInterval(NETWORK_CHECK_INTERVAL_MS)
        self.network_timer.timeout.connect(self._check_network_state)
        self.network_timer.start()
        self._save_selected_address()
        self._apply_language()
        self._refresh_address_view()
        self._refresh_connection_status()

    def closeEvent(self, event: QCloseEvent) -> None:
        self.network_timer.stop()
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
        self.use_https_label = QLabel()
        self.access_url_label = QLabel()
        self.token_label = QLabel()

        form.addRow(self.status_label, self.status_value)
        form.addRow(self.language_label, self.language_combo)
        form.addRow(self.auto_enter_label, self.auto_enter_combo)
        form.addRow(self.address_choice_label, self.address_combo)
        form.addRow(self.use_https_label, self.use_https_checkbox)

        self.url_edit.setReadOnly(True)
        form.addRow(self.access_url_label, self.url_edit)
        form.addRow(self.token_label, self.token_value)

        self.notice_label.setWordWrap(True)
        self.notice_label.setStyleSheet("color: #185abc;")
        root.addWidget(self.notice_label)

        self.security_tip_label.setWordWrap(True)
        self.security_tip_label.setStyleSheet(
            "color: #856404; background-color: #fff3cd; border: 1px solid #ffeeba; border-radius: 4px; padding: 8px;"
        )
        root.addWidget(self.security_tip_label)

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

        self.use_https_checkbox.blockSignals(True)
        self.use_https_checkbox.setChecked(self.config.use_https)
        self.use_https_checkbox.blockSignals(False)

        self.setCentralWidget(central)
        self.resize(560, 640)

    def _connect_events(self) -> None:
        self.language_combo.currentIndexChanged.connect(self._on_language_changed)
        self.auto_enter_combo.currentIndexChanged.connect(self._on_auto_enter_changed)
        self.address_combo.currentIndexChanged.connect(self._on_address_changed)
        self.use_https_checkbox.toggled.connect(self._on_use_https_changed)
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
        self.use_https_label.setText(f"{tr(language, 'use_https_label')}:")
        self.access_url_label.setText(f"{tr(language, 'access_url_label')}:")
        self.token_label.setText(f"{tr(language, 'token_label')}:")
        self.auto_enter_label.setText(f"{tr(language, 'auto_enter_label')}:")
        self.token_value.setText(tr(language, "token_enabled"))
        self.copy_button.setText(tr(language, "copy_address"))
        self.refresh_token_button.setText(tr(language, "refresh_token"))
        self.exit_button.setText(tr(language, "exit"))
        self._refresh_connection_status()

    def _access_url(self) -> str:
        protocol = "https" if self.config.use_https else "http"
        return f"{protocol}://{self.selected_address}:{self.port}/?token={self.config.token}"

    def _refresh_address_view(self) -> None:
        url = self._access_url()
        self.url_edit.setText(url)
        pixmap = QPixmap()
        pixmap.loadFromData(make_qr_png(url), "PNG")
        self.qr_label.setPixmap(
            pixmap.scaled(240, 240, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        )
        if self.config.use_https:
            self.security_tip_label.setText(tr(self.config.language, "security_tip"))
            self.security_tip_label.show()
        else:
            self.security_tip_label.hide()

    def _check_network_state(self) -> None:
        if not self.server.is_running():
            self._clear_client_connection()
            self.port = find_available_port(DEFAULT_PORT)
            self._ensure_tls_certificate()
            self.server = self._create_server()
            self.server.start()
            self._refresh_address_view()
            self._show_notice("service_restarted")

        candidates = list_address_candidates()
        addresses = {candidate.address for candidate in candidates}
        if self.selected_address in addresses:
            if self._candidate_addresses(candidates) != self._candidate_addresses(self.candidates):
                self.candidates = candidates
                self._fill_address_combo()
                if self._ensure_tls_certificate():
                    self._restart_server()
            self._refresh_connection_status()
            return

        old_address = self.selected_address
        self.candidates = candidates
        self.selected_address = choose_address(candidates, None)
        if self.selected_address == old_address:
            return

        self._fill_address_combo()
        self._ensure_tls_certificate()
        self._restart_server()
        self._clear_client_connection()
        self._save_selected_address()
        self._refresh_address_view()
        self._refresh_connection_status()
        self._show_notice("address_refreshed")

    def _candidate_addresses(self, candidates: list[AddressCandidate]) -> list[str]:
        return [candidate.address for candidate in candidates]

    def _tls_hosts(self) -> list[str]:
        return [candidate.address for candidate in self.candidates] + [self.selected_address]

    def _ensure_tls_certificate(self) -> bool:
        self.tls_paths, changed = ensure_tls_certificate(self._tls_hosts())
        return changed

    def _create_server(self) -> LocalServer:
        if self.config.use_https:
            return LocalServer(
                self.port,
                self.server_state,
                ssl_certfile=self.tls_paths.certfile,
                ssl_keyfile=self.tls_paths.keyfile,
            )
        else:
            return LocalServer(
                self.port,
                self.server_state,
                ssl_certfile=None,
                ssl_keyfile=None,
            )

    def _restart_server(self) -> None:
        self.server.stop()
        self.server = self._create_server()
        self.server.start()
        self._clear_client_connection()

    def _show_notice(self, key: str) -> None:
        self.notice_label.setText(tr(self.config.language, key))

    def _mark_client_connected(self) -> None:
        with self._lock:
            self._last_client_seen = time.monotonic()

    def _clear_client_connection(self) -> None:
        with self._lock:
            self._last_client_seen = None

    def _is_client_connected(self) -> bool:
        with self._lock:
            last_seen = self._last_client_seen
        return last_seen is not None and time.monotonic() - last_seen <= CLIENT_CONNECTED_TTL_SECONDS

    def _refresh_connection_status(self) -> None:
        if self._is_client_connected():
            self.status_value.setText(tr(self.config.language, "status_connected"))
            self.status_value.setStyleSheet("color: #1f9d55; font-weight: 600;")
        else:
            self.status_value.setText(tr(self.config.language, "status_disconnected"))
            self.status_value.setStyleSheet("color: #d33f49; font-weight: 600;")

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
        self._clear_client_connection()
        self._save_selected_address()
        self._refresh_address_view()
        self._refresh_connection_status()

    def _on_use_https_changed(self) -> None:
        use_https = self.use_https_checkbox.isChecked()
        if use_https == self.config.use_https:
            return
        with self._lock:
            self.config.use_https = use_https
            save_config(self.config)
        self._ensure_tls_certificate()
        self._restart_server()
        self._refresh_address_view()
        self._refresh_connection_status()

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
            self._last_client_seen = None
            save_config(self.config)
        self._refresh_address_view()
        self._refresh_connection_status()

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

