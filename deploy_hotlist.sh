#!/usr/bin/env bash
# 部署热榜汇总页（带原平台链接）到独立 Cloudflare Pages 项目 re-yin
# 由每日自动化（automation-1785840083224）在 generate_hotlist_html.py 之后调用
#
# 凭据来源（按优先级）：
#   1) 环境变量 CLOUDFLARE_API_TOKEN / CLOUDFLARE_ACCOUNT_ID
#   2) 仓库根目录 .cloudflare.env（已被 .gitignore 忽略，绝不入库）
# 请勿把 Token 写死在脚本里提交到 GitHub。
set -e
cd /Users/yin/WorkBuddy/热搜小程序

# 载入本地凭据（若存在）
if [ -f .cloudflare.env ]; then
  set -a
  . ./.cloudflare.env
  set +a
fi

if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
  echo "ERROR: 未找到 CLOUDFLARE_API_TOKEN。请 export 该变量，或在 .cloudflare.env 中配置（该文件已 gitignore，不会入库）。" >&2
  exit 1
fi
: "${CLOUDFLARE_ACCOUNT_ID:=b5ce389383eb935f0af6137f8a81ffdf}"

# 1) 准备纯静态站点目录：首页即汇总页，/l 为短链
rm -rf hotlist_site && mkdir -p hotlist_site/icons
cp 热搜_html/hotlist.html hotlist_site/index.html
cp -R 热搜_html/icons/. hotlist_site/icons/
printf '/l / 302\n' > hotlist_site/_redirects

# 2) 部署（CI=1 避免 wrangler 交互式提示）
export CI=1
/Users/yin/.workbuddy/binaries/node/workspace/node_modules/.bin/wrangler pages deploy hotlist_site --project-name re-yin --branch production 2>&1 | tail -15

echo "DEPLOY_DONE short_link=https://re-yin.pages.dev/l"
