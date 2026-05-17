import pyautogui
import pyperclip


def paste_text(text: str, auto_enter: str = "") -> None:
    pyperclip.copy(text)
    pyautogui.PAUSE = 0.02
    pyautogui.hotkey("ctrl", "v")
    if auto_enter:
        pyautogui.hotkey(*auto_enter.split("+"))

