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

import json

from .i18n import mobile_labels, normalize_language, tr


def render_mobile_page(language: str) -> str:
    lang = normalize_language(language)
    labels = mobile_labels(lang)
    label_json = json.dumps(labels, ensure_ascii=False)
    title = tr(lang, "product_name")
    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{title}</title>
  <style>
    * {{ box-sizing: border-box; }}
    :root {{
      --keyboard-inset: 0px;
      --footer-height: 76px;
      --page-padding: 12px;
      --bottom-space: calc(var(--page-padding) + env(safe-area-inset-bottom) + var(--keyboard-inset));
    }}
    html, body {{ height: 100%; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #15171a;
      background: #f6f7f9;
      overflow: hidden;
    }}
    .app {{
      height: 100vh;
      height: 100dvh;
      display: grid;
      grid-template-rows: auto 1fr;
      gap: 12px;
      padding: max(var(--page-padding), env(safe-area-inset-top)) var(--page-padding) calc(var(--footer-height) + var(--bottom-space));
    }}
    .topbar {{
      position: relative;
      display: flex;
      align-items: center;
      justify-content: space-between;
      min-height: 44px;
    }}
    .title {{
      position: absolute;
      left: 50%;
      transform: translateX(-50%);
      text-align: center;
      font-size: 20px;
      font-weight: 700;
      pointer-events: none;
    }}
    .clear {{
      border: 0;
      background: transparent;
      color: #72777f;
      font-size: 15px;
      padding: 8px 4px;
    }}
    textarea {{
      width: 100%;
      height: 100%;
      min-height: 0;
      resize: none;
      -webkit-user-select: text;
      user-select: text;
      border: 1px solid #d5d9df;
      border-radius: 8px;
      padding: 14px;
      font: 18px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #ffffff;
      color: #111317;
      outline: none;
    }}
    textarea:focus {{
      border-color: #1f7aec;
      box-shadow: 0 0 0 3px rgba(31, 122, 236, 0.12);
    }}
    footer {{
      position: fixed;
      left: var(--page-padding);
      right: var(--page-padding);
      bottom: var(--bottom-space);
      z-index: 10;
    }}
    .status {{
      display: flex;
      align-items: center;
      gap: 8px;
      min-height: 44px;
      font-size: 14px;
      color: #4b515a;
      overflow: hidden;
      white-space: nowrap;
      min-width: 0;
      max-width: 38%;
    }}
    .status-text {{
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .dot {{
      width: 10px;
      height: 10px;
      border-radius: 999px;
      background: #d33f49;
      flex: 0 0 auto;
    }}
    .status.connected .dot {{ background: #1f9d55; }}
    .send {{
      touch-action: manipulation;
      min-height: 52px;
      width: 100%;
      border: 0;
      border-radius: 8px;
      background: #1f7aec;
      color: #ffffff;
      font-size: 18px;
      font-weight: 700;
    }}
    .send:disabled {{
      background: #8db9f2;
    }}
    .message {{
      min-height: 20px;
      font-size: 14px;
      color: #b42318;
      text-align: center;
    }}
  </style>
</head>
<body>
  <main class="app">
    <header class="topbar">
      <div class="status" id="status"><span class="dot"></span><span class="status-text" id="statusText"></span></div>
      <div class="title">TextDrop</div>
      <button class="clear" id="clearButton" type="button"></button>
    </header>
    <textarea id="textInput" name="text" rows="8"></textarea>
    <footer>
      <div class="message" id="message"></div>
      <button class="send" id="sendButton" type="button"></button>
    </footer>
  </main>
  <script>
    const labels = {label_json};
    const timeoutMs = 3000;
    const token = new URLSearchParams(window.location.search).get("token") || "";
    const input = document.getElementById("textInput");
    const clearButton = document.getElementById("clearButton");
    const sendButton = document.getElementById("sendButton");
    const status = document.getElementById("status");
    const statusText = document.getElementById("statusText");
    const message = document.getElementById("message");
    let isComposing = false;

    clearButton.textContent = labels.clear;
    sendButton.textContent = labels.send;
    input.placeholder = labels.placeholder;

    function setConnected(isConnected) {{
      status.classList.toggle("connected", isConnected);
      statusText.textContent = isConnected ? labels.connected : labels.disconnected;
    }}

    function showMessage(text) {{
      message.textContent = text || "";
    }}

    async function fetchWithTimeout(url, options = {{}}) {{
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), timeoutMs);
      try {{
        return await fetch(url, {{ ...options, signal: controller.signal }});
      }} finally {{
        clearTimeout(timer);
      }}
    }}

    function wait(ms) {{
      return new Promise(resolve => setTimeout(resolve, ms));
    }}

    function updateKeyboardInset() {{
      if (!window.visualViewport) {{
        return;
      }}
      const inset = Math.max(0, window.innerHeight - window.visualViewport.height - window.visualViewport.offsetTop);
      document.documentElement.style.setProperty("--keyboard-inset", `${{Math.round(inset)}}px`);
    }}

    async function readCommittedInput() {{
      input.blur();
      if (isComposing) {{
        await wait(180);
      }}
      await wait(80);
      return input.value;
    }}

    async function checkConnection() {{
      try {{
        const response = await fetchWithTimeout(`/api/health?token=${{encodeURIComponent(token)}}`);
        const data = await response.json().catch(() => ({{ error: "" }}));
        setConnected(response.ok);
        return {{ ok: response.ok, error: data.error || "" }};
      }} catch (_) {{
        setConnected(false);
        return {{ ok: false, error: "" }};
      }}
    }}

    async function sendText() {{
      sendButton.disabled = true;
      sendButton.textContent = labels.sending;
      showMessage("");
      try {{
        const connection = await checkConnection();
        if (!connection.ok) {{
          showMessage(connection.error === "token_invalid" ? labels.token_invalid : labels.send_failed);
          return;
        }}

        const text = await readCommittedInput();
        const response = await fetchWithTimeout(`/api/send?token=${{encodeURIComponent(token)}}`, {{
          method: "POST",
          headers: {{ "Content-Type": "application/json" }},
          body: JSON.stringify({{ text }}),
        }});

        if (response.ok) {{
          input.value = "";
          setConnected(true);
          return;
        }}

        setConnected(false);
        const data = await response.json().catch(() => ({{ error: "" }}));
        if (data.error === "token_invalid") {{
          showMessage(labels.token_invalid);
        }} else if (data.error === "too_large") {{
          showMessage(labels.too_large);
        }} else {{
          showMessage(labels.send_failed);
        }}
      }} catch (_) {{
        setConnected(false);
        showMessage(labels.send_failed);
      }} finally {{
        sendButton.disabled = false;
        sendButton.textContent = labels.send;
      }}
    }}

    clearButton.addEventListener("click", () => {{
      input.value = "";
      input.focus();
    }});
    input.addEventListener("compositionstart", () => {{
      isComposing = true;
    }});
    input.addEventListener("compositionend", () => {{
      isComposing = false;
    }});
    sendButton.addEventListener("click", sendText);
    setConnected(false);
    checkConnection();
    setInterval(checkConnection, 5000);
    updateKeyboardInset();
    window.addEventListener("resize", updateKeyboardInset);
    if (window.visualViewport) {{
      window.visualViewport.addEventListener("resize", updateKeyboardInset);
      window.visualViewport.addEventListener("scroll", updateKeyboardInset);
    }}
  </script>
</body>
</html>"""
