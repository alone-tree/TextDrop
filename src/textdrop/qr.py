from __future__ import annotations

from io import BytesIO

import qrcode


def make_qr_png(data: str) -> bytes:
    image = qrcode.make(data)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()

