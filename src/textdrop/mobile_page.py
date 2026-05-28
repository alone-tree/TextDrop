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
    .top-actions {{
      display: flex;
      align-items: center;
      justify-content: flex-end;
      gap: 6px;
      max-width: 38%;
    }}
    .top-button {{
      border: 0;
      background: transparent;
      color: #72777f;
      font-size: 15px;
      padding: 8px 4px;
      white-space: nowrap;
    }}
    .wake-lock.active {{
      color: #1f7aec;
      font-weight: 700;
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
    .actions {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 8px;
    }}
    .action {{
      touch-action: manipulation;
      min-height: 52px;
      width: 100%;
      border-radius: 8px;
      font-size: 16px;
      font-weight: 700;
      padding: 0 8px;
      white-space: normal;
      line-height: 1.15;
    }}
    .drop-send {{
      border: 0;
      background: #1f7aec;
      color: #ffffff;
    }}
    .drop-only {{
      border: 1px solid #b7cff5;
      background: #eaf3ff;
      color: #185abc;
    }}
    .drop-send:disabled {{
      background: #8db9f2;
    }}
    .drop-only:disabled {{
      border-color: #d5d9df;
      background: #eef1f5;
      color: #7d8794;
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
      <div class="top-actions">
        <button class="top-button wake-lock" id="wakeLockButton" type="button"></button>
        <button class="top-button clear" id="clearButton" type="button"></button>
      </div>
    </header>
    <textarea id="textInput" name="text" rows="8"></textarea>
    <footer>
      <div class="message" id="message"></div>
      <div class="actions">
        <button class="action drop-send" id="dropSendLeftButton" type="button" data-apply-auto-enter="true"></button>
        <button class="action drop-only" id="dropButton" type="button" data-apply-auto-enter="false"></button>
        <button class="action drop-send" id="dropSendRightButton" type="button" data-apply-auto-enter="true"></button>
      </div>
    </footer>
  </main>
  <script>
    const labels = {label_json};
    const timeoutMs = 3000;
    const token = new URLSearchParams(window.location.search).get("token") || "";
    const input = document.getElementById("textInput");
    const wakeLockButton = document.getElementById("wakeLockButton");
    const clearButton = document.getElementById("clearButton");
    const actionButtons = Array.from(document.querySelectorAll("[data-apply-auto-enter]"));
    const status = document.getElementById("status");
    const statusText = document.getElementById("statusText");
    const message = document.getElementById("message");
    let isComposing = false;
    let wakeLock = null;
    let wakeLockWanted = false;
    let lastPointerActionAt = 0;

    wakeLockButton.textContent = labels.wake_lock_off;
    clearButton.textContent = labels.clear;
    function resetActionLabels() {{
      for (const button of actionButtons) {{
        button.textContent = button.dataset.applyAutoEnter === "true" ? labels.drop_and_send : labels.drop;
      }}
    }}

    resetActionLabels();
    input.placeholder = labels.placeholder;

    function setConnected(isConnected) {{
      status.classList.toggle("connected", isConnected);
      statusText.textContent = isConnected ? labels.connected : labels.disconnected;
    }}

    function showMessage(text) {{
      message.textContent = text || "";
    }}

    function updateWakeLockButton() {{
      wakeLockButton.classList.toggle("active", Boolean(wakeLock));
      wakeLockButton.textContent = wakeLock ? labels.wake_lock_on : labels.wake_lock_off;
    }}

    function keepInputFocused() {{
      requestAnimationFrame(() => {{
        input.focus({{ preventScroll: true }});
      }});
    }}

    async function requestScreenWakeLock() {{
      if (!wakeLockWanted || wakeLock || document.visibilityState !== "visible") {{
        return false;
      }}
      if (!("wakeLock" in navigator)) {{
        showMessage(labels.wake_lock_failed);
        updateWakeLockButton();
        return false;
      }}
      try {{
        wakeLock = await navigator.wakeLock.request("screen");
        wakeLock.addEventListener("release", () => {{
          wakeLock = null;
          updateWakeLockButton();
        }});
        showMessage("");
        updateWakeLockButton();
        return true;
      }} catch (_) {{
        wakeLock = null;
        showMessage(labels.wake_lock_failed);
        updateWakeLockButton();
        return false;
      }}
    }}

    async function toggleWakeLock() {{
      if (wakeLock) {{
        wakeLockWanted = false;
        const currentWakeLock = wakeLock;
        wakeLock = null;
        await currentWakeLock.release().catch(() => {{}});
        updateWakeLockButton();
        return;
      }}
      wakeLockWanted = true;
      await requestScreenWakeLock();
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

    function setActionsDisabled(isDisabled) {{
      for (const button of actionButtons) {{
        button.disabled = isDisabled;
      }}
    }}

    async function sendText(applyAutoEnter) {{
      setActionsDisabled(true);
      for (const button of actionButtons) {{
        button.textContent = labels.sending;
      }}
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
          body: JSON.stringify({{ text, apply_auto_enter: applyAutoEnter }}),
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
        setActionsDisabled(false);
        resetActionLabels();
        keepInputFocused();
        requestScreenWakeLock();
      }}
    }}

    function clearInput() {{
      input.value = "";
      keepInputFocused();
      requestScreenWakeLock();
    }}
    function bindTopButton(button, action) {{
      button.addEventListener("pointerdown", (event) => {{
        event.preventDefault();
      }});
      button.addEventListener("pointerup", (event) => {{
        event.preventDefault();
        lastPointerActionAt = Date.now();
        action();
      }});
      button.addEventListener("click", (event) => {{
        if (Date.now() - lastPointerActionAt < 500) {{
          event.preventDefault();
          return;
        }}
        action();
      }});
    }}
    bindTopButton(wakeLockButton, () => {{
      toggleWakeLock();
      keepInputFocused();
    }});
    bindTopButton(clearButton, clearInput);
    input.addEventListener("focus", requestScreenWakeLock);
    input.addEventListener("compositionstart", () => {{
      isComposing = true;
    }});
    input.addEventListener("compositionend", () => {{
      isComposing = false;
    }});
    function handleAction(button) {{
      if (button.disabled) {{
        return;
      }}
      keepInputFocused();
      requestScreenWakeLock();
      sendText(button.dataset.applyAutoEnter === "true");
    }}
    for (const button of actionButtons) {{
      button.addEventListener("pointerdown", (event) => {{
        event.preventDefault();
      }});
      button.addEventListener("pointerup", (event) => {{
        event.preventDefault();
        lastPointerActionAt = Date.now();
        handleAction(button);
      }});
      button.addEventListener("click", (event) => {{
        if (Date.now() - lastPointerActionAt < 500) {{
          event.preventDefault();
          return;
        }}
        handleAction(button);
      }});
    }}
    document.addEventListener("visibilitychange", () => {{
      if (document.visibilityState === "visible") {{
        requestScreenWakeLock();
      }}
    }});
    setConnected(false);
    updateWakeLockButton();
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
