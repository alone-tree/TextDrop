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

DEFAULT_PORT = 8765
MAX_TEXT_BYTES = 100 * 1024
REQUEST_TIMEOUT_SECONDS = 3
CONFIG_DIR_NAME = "TextDrop"
CONFIG_FILE_NAME = "config.json"

AUTO_ENTER_OPTIONS = [
    ("", "auto_enter_none"),
    ("enter", "auto_enter_enter"),
    ("ctrl+enter", "auto_enter_ctrl_enter"),
    ("shift+enter", "auto_enter_shift_enter"),
    ("alt+enter", "auto_enter_alt_enter"),
]

