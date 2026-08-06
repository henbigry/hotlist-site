#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
热榜速览 · 手机端界面生成器
==========================
直接通过自建 NewsNow 站（https://newsnow-yin.pages.dev）拉取多平台热榜，
内容均为各平台已审核公开的公开热榜，不再做额外敏感词过滤，
由本脚本设计一个手机端阅读比例的精美界面并填充内容，产出单文件 HTML。

用法：
    python3 generate_hotlist_html.py [--date YYYY-MM-DD]

输出：
    <OUT_ROOT>/<date>.html        当日版本
    <OUT_ROOT>/index.html         最新版（便于预览/分享）
依赖：仅标准库 + 联网（拉取热榜）
"""

import os
import sys
import json
import argparse
import datetime
import urllib.request
import urllib.error
import time
import re
import shutil

# ---------- 配置 ----------
BASE_API = "https://newsnow-yin.pages.dev/api/s?id="
OUT_ROOT = "/Users/yin/WorkBuddy/热搜小程序/热搜_html"
ICON_SRC = "/Users/yin/WorkBuddy/热搜小程序/newsnow/public/icons"
TIMEOUT = 20
RAW_PER_SOURCE = 30     # 每源最多取多少条原始候选
KEEP_PER_SOURCE = 10    # 过滤后每源保留多少条

# 目标平台（展示顺序）：id, 展示名, 站内图标文件, 主题色(hex)
# 顺序按运营需求固定；内容均为各平台已审核公开的公开热榜，不再做额外敏感词过滤。
PLATFORMS = [
    ("douyin",       "抖音",       "douyin.png",       "#fe2c55"),
    ("weibo",        "微博",       "weibo.png",        "#e6162d"),
    ("bilibili",     "哔哩哔哩",   "bilibili.png",      "#00aeec"),
    ("iqiyi",        "爱奇艺",     "iqiyi.png",        "#00be06"),
    ("sspai",        "少数派",     "sspai.png",        "#f43f5e"),
    ("toutiao",      "今日头条",   "toutiao.png",      "#e64142"),
    ("ifeng",        "凤凰网",     "ifeng.png",        "#d8362a"),
    ("thepaper",     "澎湃新闻",   "thepaper.png",     "#d8262c"),
    ("cls",          "财联社",     "cls.png",          "#c0392b"),
    ("wallstreetcn", "华尔街见闻", "wallstreetcn.png", "#b8932f"),
]

# 合规黑名单：命中即丢弃（时政/党政/国际冲突/伤亡突发事件/政策经济/社会新闻类）
# 策略：对新闻类源（凤凰/微博/知乎/财联社等）宁可多删，确保发抖音安全。

# ---------- 数据拉取 ----------
def fetch_source(sid, retries=2):
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(BASE_API + sid,
                                         headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                data = json.loads(r.read().decode("utf-8"))
            if data.get("status") in ("success", "cache"):
                out = []
                for it in data.get("items", []):
                    out.append({
                        "title": (it.get("title") or "").strip(),
                        "url": (it.get("url") or "").strip(),
                    })
                return out
        except Exception:
            pass
        if attempt < retries:
            time.sleep(1.5 ** attempt)
    return []


def clean_title(title):
    t = re.sub(r"#[^#\s]*#?", "", title)   # 去话题标签
    t = re.sub(r"\s{2,}", " ", t).strip()
    return t


def collect():
    boards = []
    for idx, (sid, name, icon, color) in enumerate(PLATFORMS):
        if idx > 0:
            time.sleep(1.5)   # 降低被限流概率
        raw = fetch_source(sid)
        items = []
        for it in raw:
            t = clean_title(it["title"])
            if not t:
                continue
            items.append({"title": t, "url": it["url"]})
            if len(items) >= KEEP_PER_SOURCE:
                break
        boards.append({
            "id": sid, "name": name, "icon": icon, "color": color,
            "total_raw": len(raw), "items": items,
        })
        status = f"{len(raw)} 原始 / {len(items)} 保留" if raw else "未取到（超时/限流）"
        print(f"      {name}: {status}")
    return boards


# ---------- 界面生成 ----------
CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=ZCOOL+KuaiLe&family=ZCOOL+XiaoWei&family=Noto+Sans+SC:wght@400;500;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
html, body {
  background: linear-gradient(160deg, #fff1e6 0%, #ffe6ef 55%, #fff7e0 100%);
  font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont,
               "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
}
body { color: #3a2f2a; line-height: 1.5; }
.phone {
  max-width: 460px; margin: 0 auto; background: #fffaf3; min-height: 100vh;
  box-shadow: 0 0 50px rgba(255,140,90,0.18);
}
/* —— 封面图（暖色 hero，占满首屏）—— */
.cover {
  position: relative; overflow: hidden;
  background: linear-gradient(135deg, #ff8a5b 0%, #ff5e8a 48%, #ffb347 100%);
  color: #fff; text-align: center;
  min-height: 100vh; min-height: 100dvh;
  display: flex; flex-direction: column;
}
.cover .cover-inner {
  flex: 1;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 86px 24px 30px;
  position: relative; z-index: 1;
}
.cover::after {
  content: ""; position: absolute; right: -40px; top: -40px;
  width: 150px; height: 150px; border-radius: 50%;
  background: rgba(255,255,255,0.16);
}
.cover::before {
  content: ""; position: absolute; left: -30px; bottom: -50px;
  width: 120px; height: 120px; border-radius: 50%;
  background: rgba(255,255,255,0.12);
}
.cover .deco { font-size: 20px; letter-spacing: 6px; opacity: 0.9; position: relative; z-index: 1; }
.cover .ctitle {
  font-family: 'ZCOOL KuaiLe';
  font-size: 36px; font-weight: 400; margin-top: 10px; letter-spacing: 2px;
  text-shadow: 0 3px 10px rgba(180,40,80,0.35); position: relative; z-index: 1;
}
.cover .cslogan {
  margin-top: 16px; display: flex; flex-direction: column; align-items: center;
  gap: 8px; position: relative; z-index: 1;
}
.cover .cslogan .s1 {
  font-family: 'ZCOOL KuaiLe';
  font-size: 20px; font-weight: 400; letter-spacing: 3px;
  text-shadow: 0 2px 8px rgba(180,40,80,0.3);
}
.cover .cslogan .s2 {
  font-size: 15px; letter-spacing: 1px; opacity: 0.96;
  font-family: 'Noto Sans SC', sans-serif;
}
.cover .cdate {
  display: inline-block; margin-top: 14px; font-size: 13px;
  background: rgba(255,255,255,0.22); padding: 6px 16px; border-radius: 20px;
  backdrop-filter: blur(4px); position: relative; z-index: 1;
}
.cover .ctag {
  display: inline-block; margin-top: 10px; font-size: 13px;
  background: rgba(255,255,255,0.22); padding: 6px 16px; border-radius: 20px;
  position: relative; z-index: 1;
}
.appbar {
  position: absolute; top: 0; left: 0; right: 0; z-index: 5;
  background: transparent;
  color: #fff; padding: 18px 20px 16px;
  text-align: left;
}
.appbar .title { font-size: 22px; letter-spacing: 1px; }
.appbar .sub { margin-top: 4px; font-size: 13px; opacity: 0.95; font-family: 'Noto Sans SC', sans-serif; }
.wrap { padding: 14px 12px 30px; }
.card {
  background: #fff7ef; border-radius: 18px; margin-bottom: 14px; overflow: hidden;
  box-shadow: 0 4px 16px rgba(255,140,90,0.12);
}
.card-head {
  display: flex; align-items: center; padding: 14px 16px;
  border-left: 5px solid var(--c);
  background: linear-gradient(90deg, color-mix(in srgb, var(--c) 10%, #fff), #fff 70%);
}
.card-head .ic { width: 32px; height: 32px; border-radius: 50%; margin-right: 10px; object-fit: contain; background: #fff; padding: 4px; border: 2px solid #fff; box-shadow: 0 1px 5px rgba(0,0,0,0.14); }
.card-head .nm { font-size: 18px; color: #2a2320; font-family: 'ZCOOL KuaiLe'; }
.card-head .tag {
  margin-left: auto; font-size: 12px; font-weight: 700; color: var(--c);
  background: color-mix(in srgb, var(--c) 14%, #fff); padding: 3px 10px; border-radius: 12px;
  font-family: 'Noto Sans SC', sans-serif;
}
.row {
  display: flex; align-items: flex-start; padding: 13px 16px;
  border-top: 1px solid #f6e7d8;
}
.row:nth-child(even) { background: #fff3e8; }
.row .rank {
  flex: 0 0 26px; height: 26px; border-radius: 50%; margin-right: 12px;
  font-size: 14px; display: flex; align-items: center; justify-content: center;
  background: #ffe7d6; color: #d9722f;
}
.row.top1 .rank { background: #ff5e8a; color: #fff; }
.row.top2 .rank { background: #ff944d; color: #fff; }
.row.top3 .rank { background: #ffc24d; color: #fff; }
.row .tt {
  flex: 1; font-size: 17px; color: #34291f; font-family: 'ZCOOL XiaoWei';
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
  text-decoration: none;
}
.row .hot { margin-left: 10px; font-size: 12px; color: #d9b89f; white-space: nowrap; flex: 0 0 auto; font-family: 'Noto Sans SC', sans-serif; }
.empty { padding: 22px 16px; color: #c9a98f; font-size: 14px; text-align: center; }
.foot {
  text-align: center; color: #c79c83; font-size: 12px; padding: 10px 20px 26px; line-height: 1.7;
  font-family: 'Noto Sans SC', sans-serif;
}
.foot b { color: #b07a55; }
""".strip()


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def build_html(date_str, boards, icon_prefix="icons/"):
    cards = []
    for b in boards:
        rows = []
        if not b["items"]:
            rows.append('<div class="empty">— 今日暂未取到内容 —</div>')
        else:
            for i, it in enumerate(b["items"], 1):
                cls = "row top%d" % i if i <= 3 else "row"
                url = it.get("url", "")
                if url:
                    ttag = ('<a class="tt" href="%s" target="_blank" '
                            'rel="noopener">%s</a>'
                            % (esc(url).replace('"', "&quot;"), esc(it["title"])))
                else:
                    ttag = '<div class="tt">%s</div>' % esc(it["title"])
                rows.append(
                    '<div class="%s"><div class="rank">%d</div>%s</div>'
                    % (cls, i, ttag)
                )
        cards.append(
            '<section class="card" style="--c:%s">'
            '<div class="card-head"><img class="ic" src="%s%s" alt="%s">'
            '<span class="nm">%s</span>'
            '<span class="tag">TOP %d</span></div>%s</section>'
            % (b["color"], icon_prefix, b["icon"], esc(b["name"]), esc(b["name"]),
               len(b["items"]), "".join(rows))
        )
    week = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    d = datetime.date.fromisoformat(date_str)
    date_cn = "%d年%d月%d日 %s" % (d.year, d.month, d.day, week[d.weekday()])
    cover = (
        '<div class="cover">'
        '<div class="appbar"><div class="title">热榜速览</div>'
        '<div class="sub">__DATE_CN__ · 全网热点一屏看全</div></div>'
        '<div class="cover-inner">'
        '<div class="deco">🌐 ✨ 🔥</div>'
        '<div class="ctitle">今日热点速览</div>'
        '<div class="cslogan"><span class="s1">打破信息茧房</span>'
        '<span class="s2">三分钟，世界发生了啥</span></div>'
        '<div class="cdate">__DATE_CN__</div>'
        '<div class="ctag">一屏看全 10 大平台</div>'
        '</div></div>'
    )
    template = (
        "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no\">"
        "<title>热榜速览 · __DATE__</title><style>__CSS__</style></head>"
        "<body><div class=\"phone\">" + cover +
        "<div class=\"wrap\">__CARDS__"
        "</div></div></body></html>"
    )
    html = (template
        .replace("__DATE__", date_str)
        .replace("__CSS__", CSS)
        .replace("__DATE_CN__", date_cn)
        .replace("__CARDS__", "".join(cards)))
    return html


def _date_cn(date_str):
    week = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    d = datetime.date.fromisoformat(date_str)
    return "%d年%d月%d日 %s" % (d.year, d.month, d.day, week[d.weekday()])


def build_links_md(date_str, boards):
    date_cn = _date_cn(date_str)
    L = [
        "# 热榜速览 · 热点详情链接（%s）" % date_cn,
        "",
        "> 内容聚合自各平台公开热榜（来源均已审核公开）。点击直达原平台该条热搜详情页。",
        "",
    ]
    for b in boards:
        L.append("## %s" % b["name"])
        if not b["items"]:
            L.append("_今日暂未取到内容_")
        else:
            for i, it in enumerate(b["items"], 1):
                L.append("%d. [%s](%s)" % (i, it["title"], it["url"]))
        L.append("")
    return "\n".join(L)


def build_links_txt(date_str, boards):
    date_cn = _date_cn(date_str)
    L = ["热榜速览 · 热点详情链接（%s）" % date_cn, ""]
    for b in boards:
        L.append("【%s】" % b["name"])
        if not b["items"]:
            L.append("（今日暂未取到内容）")
        else:
            for i, it in enumerate(b["items"], 1):
                L.append("%d. %s" % (i, it["title"]))
                L.append("   %s" % it["url"])
        L.append("")
    return "\n".join(L)


def esc_attr(s):
    return esc(s).replace('"', "&quot;")


# ---------- 汇总导航页（hotlist.html）：手机端、按平台分组、可折叠、可搜索、每条带原平台链接 ----------
HOTLIST_CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=ZCOOL+KuaiLe&family=ZCOOL+XiaoWei&family=Noto+Sans+SC:wght@400;500;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
html, body {
  background: linear-gradient(160deg, #fff1e6 0%, #ffe6ef 55%, #fff7e0 100%);
  font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
  color: #3a2f2a;
}
.phone { max-width: 460px; margin: 0 auto; background: #fffaf3; min-height: 100vh; padding-bottom: 24px; }
.hhero { background: linear-gradient(135deg, #ff8a5b 0%, #ff5e8a 48%, #ffb347 100%); color: #fff; padding: 22px 20px 18px; text-align: center; }
.hhero .ht { font-family: 'ZCOOL KuaiLe'; font-size: 24px; letter-spacing: 1px; }
.hhero .hs { font-size: 13px; opacity: 0.95; margin-top: 4px; }
.hhero .hd { display: inline-block; margin-top: 10px; font-size: 12px; background: rgba(255,255,255,0.22); padding: 4px 12px; border-radius: 14px; }
.search {
  display: block; width: calc(100% - 24px); margin: 14px auto 0; padding: 11px 14px;
  border: none; border-radius: 22px; font-size: 15px; background: rgba(255,255,255,0.94);
  color: #3a2f2a; outline: none;
}
.hlist { padding: 12px; }
.hsec {
  background: #fff7ef; border-radius: 16px; margin-bottom: 12px; overflow: hidden;
  box-shadow: 0 3px 12px rgba(255,140,90,0.1);
}
.hhead {
  display: flex; align-items: center; padding: 13px 15px; cursor: pointer;
  border-left: 5px solid var(--c);
  background: linear-gradient(90deg, color-mix(in srgb, var(--c) 10%, #fff), #fff 70%);
}
.hhead .ic { width: 28px; height: 28px; border-radius: 50%; margin-right: 9px; background: #fff; padding: 3px; border: 2px solid #fff; box-shadow: 0 1px 4px rgba(0,0,0,0.14); }
.hhead .hnm { font-family: 'ZCOOL KuaiLe'; font-size: 17px; color: #2a2320; }
.hhead .cnt { margin-left: auto; font-size: 12px; font-weight: 700; color: var(--c); background: color-mix(in srgb, var(--c) 14%, #fff); padding: 2px 9px; border-radius: 11px; margin-right: 8px; }
.hhead .chev { color: var(--c); transition: transform .2s; font-size: 13px; }
.hsec.collapsed .chev { transform: rotate(-90deg); }
.hsec.collapsed .hrows { display: none; }
.hr { display: flex; align-items: flex-start; padding: 12px 15px; text-decoration: none; color: inherit; border-top: 1px solid #f6e7d8; }
.hr:nth-child(even) { background: #fff3e8; }
.hr .rk { flex: 0 0 24px; height: 24px; border-radius: 50%; margin-right: 10px; font-size: 13px; display: flex; align-items: center; justify-content: center; background: #ffe7d6; color: #d9722f; }
.hr.top1 .rk { background: #ff5e8a; color: #fff; }
.hr.top2 .rk { background: #ff944d; color: #fff; }
.hr.top3 .rk { background: #ffc24d; color: #fff; }
.hr .ht { flex: 1; font-size: 16px; font-family: 'ZCOOL XiaoWei'; color: #34291f; line-height: 1.45; }
.hr .go { margin-left: 8px; color: #c9a98f; flex: 0 0 auto; font-size: 14px; }
.hr:active { background: #ffe9d6; }
.hempty { padding: 18px 15px; color: #c9a98f; font-size: 14px; text-align: center; }
.hfoot { text-align: center; color: #c79c83; font-size: 12px; padding: 14px 20px 26px; line-height: 1.7; }
""".strip()

HOTLIST_JS = r"""
function toggleSec(el){ el.closest('.hsec').classList.toggle('collapsed'); }
function doSearch(){
  var q = (document.getElementById('q').value || '').trim().toLowerCase();
  document.querySelectorAll('.hsec').forEach(function(sec){
    var rows = sec.querySelectorAll('.hr');
    var hit = 0;
    rows.forEach(function(r){
      var t = r.querySelector('.ht').textContent.toLowerCase();
      var ok = !q || t.indexOf(q) > -1;
      r.style.display = ok ? '' : 'none';
      if(ok) hit++;
    });
    sec.style.display = (!q || hit > 0) ? '' : 'none';
  });
}
""".strip()


def build_hotlist_html(date_str, boards):
    date_cn = _date_cn(date_str)
    sections = []
    for b in boards:
        rows = []
        if not b["items"]:
            rows.append('<div class="hempty">— 今日暂未取到 —</div>')
        else:
            for i, it in enumerate(b["items"], 1):
                cls = "hr top%d" % i if i <= 3 else "hr"
                rows.append(
                    '<a class="%s" href="%s" target="_blank" rel="noopener noreferrer">'
                    '<span class="rk">%d</span><span class="ht">%s</span>'
                    '<span class="go">↗</span></a>'
                    % (cls, esc_attr(it["url"]), i, esc(it["title"]))
                )
        sections.append(
            '<section class="hsec" data-name="%s" style="--c:%s">'
            '<div class="hhead" onclick="toggleSec(this)">'
            '<img class="ic" src="icons/%s" alt="%s">'
            '<span class="hnm">%s</span><span class="cnt">%d</span>'
            '<span class="chev">▾</span></div>'
            '<div class="hrows">%s</div></section>'
            % (esc(b["name"]), b["color"], b["icon"], esc(b["name"]),
               esc(b["name"]), len(b["items"]), "".join(rows))
        )
    total = sum(len(b["items"]) for b in boards)
    html = (
        "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no\">"
        "<title>热榜速览 · 详情导航（%s）</title><style>%s</style></head>"
        "<body><div class=\"phone\">"
        "<header class=\"hhero\"><div class=\"ht\">热榜速览 · 详情导航</div>"
        "<div class=\"hs\">打破信息茧房 · 三分钟，世界发生了啥</div>"
        "<div class=\"hd\">%s</div>"
        "<input id=\"q\" class=\"search\" placeholder=\"搜索热点关键词，快速定位 →\" oninput=\"doSearch()\">"
        "</header>"
        "<div class=\"hlist\">%s</div>"
        "<footer class=\"hfoot\">共 %d 条热点 · 按平台分类 · 点击直达原平台详情<br>"
        "内容聚合自各平台公开热榜</footer>"
        "</div><script>%s</script></body></html>"
        % (date_str, HOTLIST_CSS, date_cn, "".join(sections), total, HOTLIST_JS)
    )
    return html


def copy_icons():
    dst = os.path.join(OUT_ROOT, "icons")
    os.makedirs(dst, exist_ok=True)
    for _, _, icon, _ in PLATFORMS:
        s = os.path.join(ICON_SRC, icon)
        if os.path.exists(s):
            shutil.copy(s, os.path.join(dst, icon))


def generate(date_str):
    os.makedirs(OUT_ROOT, exist_ok=True)
    copy_icons()
    print(f"[1/3] 拉取 {len(PLATFORMS)} 个平台热榜…")
    boards = collect()
    ok = sum(1 for b in boards if b["items"])
    print(f"      {ok}/{len(boards)} 个平台取到内容")
    print("[2/3] 生成手机端界面 HTML 与链接清单 …")
    html = build_html(date_str, boards)
    path = os.path.join(OUT_ROOT, date_str + ".html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    latest = os.path.join(OUT_ROOT, "index.html")
    with open(latest, "w", encoding="utf-8") as f:
        f.write(html)
    # 链接清单（Markdown + 纯文本）
    md = build_links_md(date_str, boards)
    txt = build_links_txt(date_str, boards)
    md_path = os.path.join(OUT_ROOT, "链接清单_%s.md" % date_str)
    txt_path = os.path.join(OUT_ROOT, "链接清单_%s.txt" % date_str)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(txt)
    with open(os.path.join(OUT_ROOT, "链接清单_latest.md"), "w", encoding="utf-8") as f:
        f.write(md)
    with open(os.path.join(OUT_ROOT, "链接清单_latest.txt"), "w", encoding="utf-8") as f:
        f.write(txt)
    # 汇总导航页（手机端、按平台分组、每条带原平台直达链接）
    hotlist = build_hotlist_html(date_str, boards)
    hotlist_path = os.path.join(OUT_ROOT, "hotlist.html")
    with open(hotlist_path, "w", encoding="utf-8") as f:
        f.write(hotlist)
    # 导出 boards 供归档脚本复用：保证归档快照与当日线上页数据一致，且避免重复拉取
    boards_path = os.path.join(OUT_ROOT, "boards_%s.json" % date_str)
    with open(boards_path, "w", encoding="utf-8") as f:
        json.dump(boards, f, ensure_ascii=False)
    print(f"[3/3] 完成 ✅")
    print(f"      当日 HTML : {path}")
    print(f"      最新 HTML : {latest}")
    print(f"      链接清单  : {md_path}")
    print(f"                : {txt_path}")
    print(f"      汇总页    : {hotlist_path}")
    return path, latest, md_path, txt_path, hotlist_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=datetime.date.today().strftime("%Y-%m-%d"))
    args = ap.parse_args()
    generate(args.date)


if __name__ == "__main__":
    main()
