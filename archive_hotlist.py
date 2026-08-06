#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热榜归档脚本
===========
读取 generate_hotlist_html.py 当日产出的 boards_<date>.json（与线上页同源同数据），
渲染一份独立命名的手机端快照到 hotlist-archive/days/YYYY-MM-DD-<随机>.html，
并重建 hotlist-archive/index.html 历史索引页（按日期倒序，可在线回看任意一天）。

用法：
    python3 archive_hotlist.py [--date YYYY-MM-DD]

设计要点：
  - 文件名带 8 位随机扰动（secrets.token_hex(4)），同日多次运行互不覆盖，且不易被预测。
  - 图标用相对路径 ../icons/，快照放在 days/ 子目录，保持仓库根目录清爽。
  - 与线上页共用同一份 boards 数据，归档快照 == 当日线上页内容，绝不二次拉取。
"""

import os
import sys
import json
import argparse
import datetime
import secrets
import shutil

ROOT = "/Users/yin/WorkBuddy/热搜小程序"
OUT_ROOT = os.path.join(ROOT, "热搜_html")
ARCHIVE = os.path.join(ROOT, "hotlist-archive")
DAYS = os.path.join(ARCHIVE, "days")
ICON_DST = os.path.join(ARCHIVE, "icons")

sys.path.insert(0, ROOT)
import generate_hotlist_html as gh  # noqa: E402


def load_boards(date_str):
    p = os.path.join(OUT_ROOT, "boards_%s.json" % date_str)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    print("  [归档] 未找到 boards_%s.json，重新拉取…" % date_str)
    return gh.collect()


def copy_icons():
    os.makedirs(ICON_DST, exist_ok=True)
    for _, _, icon, _ in gh.PLATFORMS:
        s = os.path.join(gh.ICON_SRC, icon)
        if os.path.exists(s):
            shutil.copy(s, os.path.join(ICON_DST, icon))


def week_cn(date_str):
    wk = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    d = datetime.date.fromisoformat(date_str)
    return "%d年%d月%d日 %s" % (d.year, d.month, d.day, wk[d.weekday()])


def build_index():
    files = sorted(
        [f for f in os.listdir(DAYS) if f.endswith(".html")],
        reverse=True,
    )
    items = []
    for fn in files:
        d = fn[:10]  # YYYY-MM-DD
        try:
            dc = week_cn(d)
        except Exception:
            dc = d
        items.append(
            '<a class="aitem" href="days/%s"><span class="adate">%s</span>'
            '<span class="abadge">查看快照 →</span></a>' % (fn, dc)
        )
    count = len(files)
    tpl = (
        "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, "
        "maximum-scale=1, user-scalable=no\">"
        "<title>热榜速览 · 历史归档</title>"
        "<style>"
        "@import url('https://fonts.googleapis.com/css2?family=ZCOOL+KuaiLe&family=Noto+Sans+SC:wght@400;500;700&display=swap');"
        "* { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }"
        "html, body { background: linear-gradient(160deg, #fff1e6 0%, #ffe6ef 55%, #fff7e0 100%);"
        " font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, \"PingFang SC\", "
        "\"Microsoft YaHei\", sans-serif; color: #3a2f2a; }"
        ".phone { max-width: 460px; margin: 0 auto; background: #fffaf3; min-height: 100vh; padding-bottom: 24px; }"
        ".ahero { background: linear-gradient(135deg, #ff8a5b 0%, #ff5e8a 48%, #ffb347 100%);"
        " color: #fff; padding: 26px 20px 20px; text-align: center; }"
        ".ahero .at { font-family: 'ZCOOL KuaiLe'; font-size: 25px; letter-spacing: 1px; }"
        ".ahero .as { font-size: 13px; opacity: 0.95; margin-top: 6px; }"
        ".alist { padding: 14px 12px; }"
        ".aitem { display: flex; align-items: center; padding: 15px 16px; margin-bottom: 10px;"
        " background: #fff7ef; border-radius: 14px; text-decoration: none; color: #3a2f2a;"
        " box-shadow: 0 3px 12px rgba(255,140,90,0.1); border-left: 5px solid #ff7a59; }"
        ".aitem:active { background: #ffe9d6; }"
        ".aitem .adate { font-family: 'ZCOOL KuaiLe'; font-size: 17px; }"
        ".aitem .abadge { margin-left: auto; font-size: 13px; font-weight: 700; color: #ff5e8a;"
        " background: #ffe3ec; padding: 4px 10px; border-radius: 12px; }"
        ".afoot { text-align: center; color: #c79c83; font-size: 12px; padding: 14px 20px 26px; line-height: 1.7; }"
        "</style></head><body><div class=\"phone\">"
        "<header class=\"ahero\"><div class=\"at\">热榜速览 · 历史归档</div>"
        "<div class=\"as\">每日热点快照 · 共 [[COUNT]] 份 · 点击回看任意一天</div></header>"
        "<div class=\"alist\">[[ITEMS]]</div>"
        "<footer class=\"afoot\">内容聚合自各平台公开热榜<br>"
        "仅供参考</footer>"
        "</div></body></html>"
    )
    return tpl.replace("[[COUNT]]", str(count)).replace("[[ITEMS]]", "".join(items))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.date.today().strftime("%Y-%m-%d"))
    args = ap.parse_args()
    date_str = args.date

    os.makedirs(DAYS, exist_ok=True)
    print("[归档 1/3] 载入当日 boards 数据…")
    boards = load_boards(date_str)
    ok = sum(1 for b in boards if b["items"])
    print("      %d/%d 个平台有内容" % (ok, len(boards)))

    print("[归档 2/3] 渲染快照 + 拷贝图标…")
    copy_icons()
    html = gh.build_html(date_str, boards, icon_prefix="../icons/")
    rand = secrets.token_hex(4)  # 8 位随机，避免同日重复 / 被预测
    snap_name = "%s-%s.html" % (date_str, rand)
    snap_path = os.path.join(DAYS, snap_name)
    with open(snap_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("      快照: %s" % snap_path)

    print("[归档 3/3] 重建历史索引页…")
    idx = build_index()
    idx_path = os.path.join(ARCHIVE, "index.html")
    with open(idx_path, "w", encoding="utf-8") as f:
        f.write(idx)
    print("      索引: %s" % idx_path)
    print("完成 ✅ 本次快照文件名: %s" % snap_name)


if __name__ == "__main__":
    main()
