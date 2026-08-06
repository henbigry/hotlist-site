#!/usr/bin/env bash
# 归档站部署：把 hotlist-archive 提交并 push 到 GitHub，再部署到独立 Cloudflare Pages 项目 re-yin-archive
# 由每日自动化（automation-1785840083224）在 generate_hotlist_html.py + archive_hotlist.py 之后调用
#
# 凭据来源：仓库根目录 .github.env（已被 .gitignore 忽略，绝不入库）
#   GITHUB_TOKEN / GITHUB_USER / ARCHIVE_REPO
# 请勿把 Token 写死在脚本里提交到 GitHub。
set -e
cd /Users/yin/WorkBuddy/热搜小程序

if [ -f .github.env ]; then
  set -a
  . ./.github.env
  set +a
fi
# Cloudflare 部署需要 CLOUDFLARE_API_TOKEN / CLOUDFLARE_ACCOUNT_ID
if [ -f .cloudflare.env ]; then
  set -a
  . ./.cloudflare.env
  set +a
fi

if [ -z "$GITHUB_TOKEN" ] || [ -z "$GITHUB_USER" ] || [ -z "$ARCHIVE_REPO" ]; then
  echo "ERROR: .github.env 缺少 GITHUB_TOKEN / GITHUB_USER / ARCHIVE_REPO" >&2
  exit 1
fi

cd hotlist-archive

# 仅在确有改动时提交（含未跟踪的新快照/图标/索引）
if [ -z "$(git status --porcelain)" ]; then
  echo "ARCHIVE_CLEAN: 无改动，跳过 commit/push"
else
  git add -A
  git -c user.name="hotlist-bot" -c user.email="bot@hotlist.local" \
    commit -m "archive: $(date +%Y-%m-%d) 自动归档快照"
  # 用 token 注入 remote URL，避免非交互环境下的凭据弹窗
  git push "https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${ARCHIVE_REPO}.git" main
  echo "PUSH_DONE"
fi

# 部署到独立归档 Pages 项目（项目需预先存在；首次由 setup 阶段用 Cloudflare API 创建）
# 注意：项目 production_branch=main，故此处 --branch 必须填 main，默认域名才会服务该部署
export CI=1
/Users/yin/.workbuddy/binaries/node/workspace/node_modules/.bin/wrangler pages deploy . \
  --project-name re-yin-archive --branch main 2>&1 | tail -15

echo "DEPLOY_DONE archive_url=https://re-yin-archive.pages.dev"
