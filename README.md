# AnyRouter 自动签到

一个可部署到 GitHub Actions 的 AnyRouter 自动签到脚本。凭证通过环境变量或 GitHub Secrets 提供，不需要写进代码。

## 文件

- `checkin.py`: 签到脚本，使用 Python 标准库，无需安装依赖。
- `.github/workflows/checkin.yml`: GitHub Actions 定时任务，每天北京时间 08:10 运行，也支持手动运行。
- `.env.example`: 本地运行时可参考的环境变量模板。

## GitHub Actions 使用

1. 新建一个 GitHub 仓库，把这些文件推送上去。
2. 进入仓库 `Settings` -> `Secrets and variables` -> `Actions` -> `New repository secret`。
3. 至少添加下面其中一个凭证：
   - `ANYROUTER_COOKIE`: 登录 AnyRouter 后浏览器请求里的 Cookie。
   - `ANYROUTER_AUTHORIZATION`: 如果站点使用 Bearer Token，也可以填这个。
4. 可选添加：
   - `ANYROUTER_BASE_URL`: 默认 `https://anyrouter.top`。
   - `ANYROUTER_CHECKIN_PATH`: 默认 `/api/user/sign_in`。
   - `ANYROUTER_INFO_PATH`: 默认 `/api/v1/user/info`，不需要查询用户信息可设为空。
   - `ANYROUTER_NEW_API_USER`: 如请求头里有 `new-api-user`，可填对应用户 ID。
   - `SERVERCHAN_SENDKEY`: Server 酱通知。
   - `PUSHPLUS_TOKEN`: PushPlus 通知。
5. 到 `Actions` 页面启用 workflow，可点 `Run workflow` 手动测试一次。

## 本地运行

PowerShell 示例：

```powershell
$env:ANYROUTER_COOKIE = "你的 Cookie"
python checkin.py
```

如果接口路径和默认值不同，可以额外设置：

```powershell
$env:ANYROUTER_BASE_URL = "https://你的站点域名"
$env:ANYROUTER_CHECKIN_PATH = "/api/user/sign_in"
$env:ANYROUTER_INFO_PATH = "/api/v1/user/info"
python checkin.py
```

## 获取 Cookie

1. 在浏览器登录 AnyRouter。
2. 按 `F12` 打开开发者工具，进入 `Network`。
3. 刷新页面或手动点击签到。
4. 找到请求，复制 Request Headers 里的 `Cookie`。
5. 把 Cookie 保存为 GitHub Secret：`ANYROUTER_COOKIE`。

## 说明

脚本默认按 AnyRouter 当前接口 `/api/user/sign_in` 发送 POST 请求，并使用空请求体。如果 AnyRouter 当前接口有变化，只需要调整 `ANYROUTER_CHECKIN_PATH`，不用改代码。

