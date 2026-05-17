import pyautogui
import pyperclip


def paste_text(text: str) -> None:
    pyperclip.copy(text)
    pyautogui.PAUSE = 0.02
    pyautogui.hotkey("ctrl", "v")

