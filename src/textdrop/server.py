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

import asyncio
import json
import threading
from dataclasses import dataclass
from typing import Callable

import uvicorn
from fastapi import FastAPI, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse

from .constants import MAX_TEXT_BYTES
from .mobile_page import render_mobile_page


@dataclass
class ServerState:
    get_token: Callable[[], str]
    get_language: Callable[[], str]
    get_auto_enter: Callable[[], str]
    paste_text: Callable[[str, str], None]


def create_app(state: ServerState) -> FastAPI:
    app = FastAPI()

    @app.get("/", response_class=HTMLResponse)
    async def index() -> str:
        return render_mobile_page(state.get_language())

    @app.get("/api/health")
    async def health(token: str = Query(default="")) -> JSONResponse:
        if token != state.get_token():
            return JSONResponse({"ok": False, "error": "token_invalid"}, status_code=403)
        return JSONResponse({"ok": True, "language": state.get_language()})

    @app.post("/api/send")
    async def send(request: Request, token: str = Query(default="")) -> JSONResponse:
        if token != state.get_token():
            return JSONResponse({"ok": False, "error": "token_invalid"}, status_code=403)

        raw = await request.body()
        try:
            payload = json.loads(raw.decode("utf-8")) if raw else {"text": ""}
        except json.JSONDecodeError:
            return JSONResponse({"ok": False, "error": "bad_request"}, status_code=400)

        text = payload.get("text", "")
        if not isinstance(text, str):
            return JSONResponse({"ok": False, "error": "bad_request"}, status_code=400)
        if len(text.encode("utf-8")) > MAX_TEXT_BYTES:
            return JSONResponse({"ok": False, "error": "too_large"}, status_code=413)

        apply_auto_enter = payload.get("apply_auto_enter", True)
        if not isinstance(apply_auto_enter, bool):
            return JSONResponse({"ok": False, "error": "bad_request"}, status_code=400)

        try:
            auto_enter = state.get_auto_enter() if apply_auto_enter else ""
            await asyncio.to_thread(state.paste_text, text, auto_enter)
        except Exception:
            return JSONResponse({"ok": False, "error": "paste_failed"}, status_code=500)

        return JSONResponse({"ok": True})

    return app


class LocalServer:
    def __init__(self, port: int, state: ServerState):
        self.port = port
        self._server = uvicorn.Server(
            uvicorn.Config(
                create_app(state),
                host="0.0.0.0",
                port=port,
                log_level="warning",
                access_log=False,
                log_config=None,
            )
        )
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self._thread = threading.Thread(target=self._server.run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._server.should_exit = True
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)
