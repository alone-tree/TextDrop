# TextDrop

TextDrop 是一个轻量级跨设备输入工具。用户可以在手机浏览器中输入文字，点击发送后，文本会通过 Windows 端程序粘贴到当前光标所在位置。

## 核心功能

- Windows 端运行桌面 GUI。当前仅支持Windows端，Mac端后续会增加适配。
- 手机端任意系统都可用，能扫描二维码即可，无需安装 App。微信扫码可行，但推荐在手机浏览器中使用。
- 发送文本时会覆盖系统剪贴板，并模拟 `Ctrl+V`。
- 手机端提供“投递”和“投递并发送”两种按钮。“投递”只粘贴文本；“投递并发送”会在粘贴后按 Windows 主界面配置的追加按键（Enter / Ctrl+Enter / Shift+Enter / Alt+Enter，默认关闭）。
- 不保存发送历史，不记录正文，不恢复原剪贴板。
- 不做云端连接、账号系统、托盘常驻和开机自启。
- v0.1.1 只支持同一局域网内使用，跨网络的云端支持后期根据需求上线。

## 使用说明

1. 解压 `TextDrop-v0.1-windows.zip`。
2. 在解压后的 `TextDrop` 文件夹里启动 `TextDrop.exe`。
3. 首次使用如果 Windows 防火墙弹出提示，请允许专用网络访问。
4. 用手机扫描 Windows 主界面中的二维码。
5. 在手机页面输入文本。
6. 在电脑上点击目标输入框，让光标停在要输入的位置。
7. 点击手机页面底部的“投递”，或点击左右两侧的“投递并发送”。

如果电脑同时开启 VPN、系统代理或虚拟网卡，手机可能无法访问自动选择的地址。此时请在 Windows 主界面的地址下拉框里切换到与手机处于同一网络的地址，然后重新扫码。

## 配置位置

配置文件默认保存到：

```text
%APPDATA%\TextDrop\config.json
```

配置包含 Token、语言设置和最近选择的地址。刷新 Token 后旧二维码和旧链接会失效，需要重新扫码。

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

打包前需要先关闭正在运行的 TextDrop，否则 Windows 可能占用 `dist` 目录中的依赖文件，导致构建脚本无法删除旧产物。

发布时优先使用 zip。用户解压后运行文件夹里的 `TextDrop.exe`，不要把 `TextDrop.exe` 单独移动出来，否则依赖文件缺失会导致程序无法运行。但可以复制`TextDrop.exe`的快捷方式，或者添加到任务栏，便于启动。



## 许可证

本项目采用 **GNU Affero General Public License v3 (AGPL v3)** 开源协议。

- 个人使用、学习、修改均不受限制。
- 禁止将本软件或修改后的版本以闭源形式发布或销售。
- 禁止将本软件作为网络服务提供而不开放源代码。
- 版权所有人保留额外授权的权利。

> 商业使用请联系作者授权。

---

如果这个工具对你有帮助，欢迎打赏、点赞、分享使用心得~

![1779018162312](image/README/1779018162312.png)
