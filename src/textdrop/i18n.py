from __future__ import annotations


LANGUAGE_OPTIONS = [("zh", "中文"), ("en", "English")]

TEXT = {
    "zh": {
        "window_title": "TextDrop",
        "product_name": "TextDrop",
        "status_label": "状态",
        "status_running": "正在运行",
        "status_closed": "已关闭",
        "language_label": "语言",
        "address_choice_label": "地址",
        "access_url_label": "手机访问地址",
        "token_label": "Token",
        "token_enabled": "已启用",
        "copy_address": "复制地址",
        "refresh_token": "刷新 Token",
        "exit": "退出",
        "confirm_refresh_title": "确认刷新 Token",
        "confirm_refresh_message": "刷新后旧链接将失效，请再次扫码连接。",
        "clear": "清空",
        "send": "发送到电脑",
        "sending": "发送中...",
        "connected": "连接成功",
        "disconnected": "未连接",
        "placeholder": "在这里输入文字...",
        "send_failed": "发送失败，请确认电脑端正在运行",
        "token_invalid": "连接已失效，请重新扫码",
        "too_large": "内容过长，请分段发送",
        "auto_enter_label": "粘贴后按键",
        "auto_enter_none": "不自动按键",
        "auto_enter_enter": "Enter",
        "auto_enter_ctrl_enter": "Ctrl + Enter",
        "auto_enter_shift_enter": "Shift + Enter",
        "auto_enter_alt_enter": "Alt + Enter",
    },
    "en": {
        "window_title": "TextDrop",
        "product_name": "TextDrop",
        "status_label": "Status",
        "status_running": "Running",
        "status_closed": "Closed",
        "language_label": "Language",
        "address_choice_label": "Address",
        "access_url_label": "Phone URL",
        "token_label": "Token",
        "token_enabled": "Enabled",
        "copy_address": "Copy URL",
        "refresh_token": "Refresh Token",
        "exit": "Exit",
        "confirm_refresh_title": "Refresh Token",
        "confirm_refresh_message": "Old links will stop working. Scan the QR code again after refreshing.",
        "clear": "Clear",
        "send": "Send to computer",
        "sending": "Sending...",
        "connected": "Connected",
        "disconnected": "Offline",
        "placeholder": "Type text here...",
        "send_failed": "Send failed. Check that TextDrop is running on the computer.",
        "token_invalid": "Connection expired. Scan the QR code again.",
        "too_large": "Text is too long. Send it in smaller parts.",
        "auto_enter_label": "Auto key after paste",
        "auto_enter_none": "No auto key",
        "auto_enter_enter": "Enter",
        "auto_enter_ctrl_enter": "Ctrl + Enter",
        "auto_enter_shift_enter": "Shift + Enter",
        "auto_enter_alt_enter": "Alt + Enter",
    },
}


def normalize_language(language: str | None) -> str:
    return language if language in TEXT else "zh"


def tr(language: str | None, key: str) -> str:
    lang = normalize_language(language)
    return TEXT[lang][key]


def mobile_labels(language: str | None) -> dict[str, str]:
    lang = normalize_language(language)
    keys = [
        "clear",
        "send",
        "sending",
        "connected",
        "disconnected",
        "placeholder",
        "send_failed",
        "token_invalid",
        "too_large",
    ]
    return {key: TEXT[lang][key] for key in keys}
