# TextDrop

TextDrop 是一个轻量级跨设备输入工具。用户可以在手机浏览器中输入文字，点击发送后，文本会通过 Windows 端程序粘贴到当前光标所在位置。

## 当前版本

v0.1 只支持同一局域网内使用：

- Windows 端运行桌面 GUI。
- 手机端使用浏览器访问，无需安装 App。
- 发送文本时会覆盖系统剪贴板，并模拟 `Ctrl+V`。
- 发送成功后不会自动按 Enter，也不会自动提交目标应用中的输入框。
- 不保存发送历史，不记录正文，不恢复原剪贴板。
- 不做云端连接、账号系统、托盘常驻和开机自启。

## 开发运行

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m textdrop
```

## 打包便携版 zip

```powershell
.\scripts\build.ps1
```

打包产物会生成：

- `dist\TextDrop-v0.1-windows\TextDrop\TextDrop.exe`
- `dist\TextDrop-v0.1-windows.zip`

发布时优先使用 zip。用户解压后运行文件夹里的 `TextDrop.exe`，不要把 `TextDrop.exe` 单独移动出来，否则依赖文件缺失会导致程序无法运行。

打包前需要先关闭正在运行的 TextDrop，否则 Windows 可能占用 `dist` 目录中的依赖文件，导致构建脚本无法删除旧产物。

## 使用说明

1. 解压 `TextDrop-v0.1-windows.zip`。
2. 在解压后的 `TextDrop` 文件夹里启动 `TextDrop.exe`。
3. 首次使用如果 Windows 防火墙弹出提示，请允许专用网络访问。
4. 用手机扫描 Windows 主界面中的二维码。
5. 在手机页面输入文本。
6. 在电脑上点击目标输入框，让光标停在要输入的位置。
7. 点击手机页面底部的“发送到电脑”。

如果电脑同时开启 VPN、系统代理或虚拟网卡，手机可能无法访问自动选择的地址。此时请在 Windows 主界面的地址下拉框里切换到与手机处于同一网络的地址，然后重新扫码。

## 配置位置

配置文件默认保存到：

```text
%APPDATA%\TextDrop\config.json
```

配置包含 Token、语言设置和最近选择的地址。刷新 Token 后旧二维码和旧链接会失效，需要重新扫码。
