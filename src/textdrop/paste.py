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

import pyautogui
import pyperclip


def paste_text(text: str, auto_enter: str = "") -> None:
    pyperclip.copy(text)
    pyautogui.PAUSE = 0.02
    pyautogui.hotkey("ctrl", "v")
    if auto_enter:
        pyautogui.hotkey(*auto_enter.split("+"))

