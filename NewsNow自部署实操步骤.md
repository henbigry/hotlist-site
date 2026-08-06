# NewsNow 自部署实操步骤（Cloudflare Pages）

> 目标：半小时内拥有自己的热榜聚合站，免费、零合规风险、完整保留"点标题跳原平台"体验。
> 适用版本：ourongxing/newsnow（newsnow.busiyi.world 同款，MIT 协议，20k+ star）。轻量替代见末尾。

---

## 前置条件
- **GitHub 账号**（免费）
- **Cloudflare 账号**（免费，用于 Pages + D1 数据库）
- 本地 **Node.js >= 20**（仅本地调试需要，纯云端部署可不装）
- 自定义域名 + **ICP 备案**（可选；国内正常访问、以及后续挂小程序 / 抖音 web-view 才必须）

---

## 步骤

### 1. Fork 仓库
- 打开 https://github.com/ourongxing/newsnow
- 点右上角 **Fork** →  Fork 到你自己的 GitHub 账号。

### 2. Cloudflare Pages 导入
- 登录 Cloudflare 控制台 → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**。
- 授权并选择你刚 Fork 的 `newsnow` 仓库。

### 3. 构建设置（关键，照填）
| 项 | 值 |
|---|---|
| Build command | `pnpm run build` |
| Output directory | `dist/output/public` |
| Node 版本 | 20+（CF 默认即可，无需改） |

### 4. 创建 D1 数据库
- Cloudflare 控制台 → **D1** → **Create database**。
- 记下 **database_id** 和 **database name**（下一步要填）。

### 5. 绑定 D1 到 Pages
- 进入 Pages 项目 → **Settings** → **Functions** → **D1 database bindings**。
- 新建绑定，选择第 4 步的数据库（绑定变量名按仓库 `example.wrangler.toml` 模板，通常为 `DB`）。
- 也可在项目根把 `example.wrangler.toml` 复制为 `wrangler.toml`，填入 `database_id` / `database_name`，部署时自动生效。

### 6. 配置环境变量（生产环境）
Pages 项目 → **Settings** → **Environment variables** → 生产环境：
| 变量 | 值 | 说明 |
|---|---|---|
| `INIT_TABLE` | `true` | **首次部署必须**，跑完建表后可改 `false` |
| `ENABLE_CACHE` | `true` | 开启缓存，避免频繁抓取被源站封 IP |
| `G_CLIENT_ID` | （可选） | 仅需要 GitHub 登录功能时填 |
| `G_CLIENT_SECRET` | （可选） | 同上 |
| `JWT_SECRET` | （可选） | 同上，通常与 Secret 相同 |

> 本地调试时：把 `example.env.server` 复制为 `.env.server` 再填。

### 7. 部署
- 保存设置 → 回到 **Deployments** → **Retry deployment**（或推送一次触发构建）。
- 等待构建完成，CF 会分配 `https://<项目名>.pages.dev` 域名。

### 8. 初始化数据库
- 首次访问你的 `*.pages.dev` 域名，因 `INIT_TABLE=true`，会自动建表。
- 确认各平台热榜正常加载后，可将 `INIT_TABLE` 改回 `false`（避免重复建表开销）。

### 9. （可选）自定义域名
- Pages 项目 → **Custom domains** → 填写你**已 ICP 备案**的域名。
- 按提示在域名 DNS 加 CNAME。
- 国内用户访问、以及后续接小程序 / 抖音 web-view，都必须用已备案域名。

### 10. 维护
- 关注原仓库更新，定期同步 Fork（或自己 fork 后不再跟随）。
- 个别源站改版可能导致对应榜单失效，按需自行修源或等社区修。

---

## 轻量替代方案
- **不想折腾 D1 / OAuth**：用 `bello96/newsnow` Fork——已移除登录/搜索，精简到 12 个源，部署更简单（同样 CF Pages + D1）。
- **想自己掌控服务器**：Docker 自托管——仓库根目录 `docker compose up`，环境变量写在 `docker-compose.yml`。

---

## 验证上线
- [ ] 打开 `*.pages.dev`，确认百度 / B站 / 抖音 / 财联社等多平台热榜加载。
- [ ] 确认缓存生效（重复刷新不报错、间隔拉取）。
- [ ] 手机浏览器打开，体验"刷到即知"；点标题能跳原平台。

---

## 与抖音号 / 小程序衔接
- **抖音号**：把这个站作为"完整版 / 实时版"落点，bio 引流，形成「抖音获客 → 网站沉淀」闭环。
- **小程序（未来）**：本站即现成后端 API；接小程序时需①已备案域名 ②微信 `request` 合法域名白名单 ③微信内容安全 API 做敏感词过滤。

---

### 备注
我（产品通）可以协助执行 Cloudflare 侧的部署动作——当你把 GitHub / Cloudflare 账号授权给我（或提供 API Token）后，我可直接在终端跑 Fork、配置、部署流程。当前文档已可让你自己 30 分钟内独立完成。
