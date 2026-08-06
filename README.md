# 热榜速览 · 汇总站

抖音热榜号配套的「图片引流 → 短链 → 汇总页 → 原平台详情」承接层。

## 站点

- 汇总页（手机端）：`https://re-yin.pages.dev/`
- 短链（置顶评论用）：`https://re-yin.pages.dev/l` （302 → 汇总页）

## GitHub 仓库

- 本仓库（热搜汇总站：代码 / 产物 / 部署脚本）：`https://github.com/henbigry/hotlist-site`
- newsnow 新闻站（独立仓库，fork 自 ourongxing/newsnow）：`https://github.com/henbigry/newsnow`
  - 本地 `newsnow/` 的 `origin` = 你的 fork，`upstream` = 官方源。改完新闻站后 `git push` 推到你的 fork。
  - 同步官方更新：`git fetch upstream && git merge upstream/main`

## 仓库结构

本仓库管理「热搜汇总站」的自定义代码。`newsnow/` 新闻站是**独立仓库**（fork 自 ourongxing/newsnow），已在本仓库 `.gitignore` 中忽略。

```
热搜小程序/
├── generate_hotlist_html.py   # 主生成器：拉取 10 平台热榜 + 敏感词过滤 + 生成界面/链接/汇总页
├── _screenshot_custom_html.py # 把生成的 HTML 截成手机端 PNG（封面 + 10 平台卡片）
├── deploy_hotlist.sh          # 部署 hotlist_site/ 到 Cloudflare Pages（re-yin）
├── 热搜_html/                 # 生成产物：index.html、链接清单_*.md/txt、hotlist.html
├── hotlist_site/             # 待部署的纯静态站点（首页=汇总页）
├── .cloudflare.env           # 本地 Cloudflare 凭据（gitignore，不入库）
└── .gitignore
```

10 个平台：百度、哔哩哔哩、财联社、豆瓣、抖音、虎扑、爱奇艺、凤凰网、微博、知乎。

## 本地改动 → 提交 → 部署 工作流

```bash
# 1) 拉取最新（若多人协作）
git pull

# 2) 改代码（如调整 generate_hotlist_html.py 的样式 / 敏感词库 / 平台列表）
#    - 敏感词过滤：SENSITIVE 列表
#    - 平台与图标：PLATFORMS 列表（id, 名称, 图标, 主题色）
#    - 样式：CSS 变量 / .cover / .card 等

# 3) 重新生成（需联网拉取热榜，用 Bash 关闭沙箱）
/Users/yin/.workbuddy/binaries/python/envs/default/bin/python generate_hotlist_html.py

# 4) 提交
git add -A && git commit -m "feat: ..." && git push

# 5) 部署（依赖 .cloudflare.env 或环境变量中的 CLOUDFLARE_API_TOKEN）
bash deploy_hotlist.sh
```

每日 08:00 自动化（automation-1785840083224）会自动执行第 3、5 步：生成界面 + 链接清单 + 汇总页，并部署，输出短链供你置顶评论。

## 合规提示

汇总页与图片均经过敏感词过滤，但仍建议发布前人工复核。涉及时政/国际冲突/伤亡类内容在抖音有被限流风险。
