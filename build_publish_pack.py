#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成「抖音发布包」：在每日截图产物基础上，产出一份可直接照抄的发布文案
（正文 + 置顶评论 + 图片顺序），输出到 热搜_html_shots/发布文案.md。

运行时机：截图脚本 _screenshot_custom_html.py 之后（图片已按 0-cover / 1-抖音 … 命名）。
日期与 generate_hotlist_html.py 保持一致（本地 today）。
"""
import datetime, os, re

SHOTS = "/Users/yin/WorkBuddy/热搜小程序/热搜_html_shots"
SHORT_LINK = "https://re-yin.pages.dev/l"
OUT_MD = os.path.join(SHOTS, "发布文案.md")

PLATFORM_DESC = "抖音 · 微博 · B站 · 爱奇艺 · 少数派 · 今日头条 · 凤凰 · 澎湃 · 财联社 · 华尔街见闻"


def date_cn(date_str):
    y, m, d = date_str.split("-")
    return f"{int(y)}年{int(m)}月{int(d)}日"


def scan_images():
    """扫描截图目录，按文件名前缀数字升序返回 png 列表。"""
    files = [f for f in os.listdir(SHOTS) if f.lower().endswith(".png")]
    def key(name):
        m = re.match(r"(\d+)-", name)
        return (int(m.group(1)) if m else 999, name)
    return sorted(files, key=key)


def build(date_str):
    imgs = scan_images()
    dc = date_cn(date_str)

    lines = []
    lines.append(f"# 抖音发布文案 · {dc}\n")
    lines.append("## ✏️ 正文（直接复制粘贴到抖音）\n")
    lines.append("```")
    lines.append(f"📌 今日全网热榜速览（{date_str}）")
    lines.append("")
    lines.append("一张图带你看懂今天全网都在聊什么 👇")
    lines.append(f"{PLATFORM_DESC}，10 大平台热点一次看够。")
    lines.append("")
    lines.append("某条热搜想看原平台详情？每张图都附了直达链接 👉")
    lines.append(f"🔗 完整榜单 + 原链接：{SHORT_LINK}")
    lines.append("")
    lines.append("#热搜 #每日热榜 #今天的热搜 #资讯 #热点速览")
    lines.append("```\n")

    lines.append("## 📌 置顶评论（发布后设为置顶）\n")
    lines.append("```")
    lines.append(f"完整热榜 + 每条热搜的原平台直达链接都在这 👉 {SHORT_LINK}")
    lines.append("（图片勾起的好奇心，这里一次满足 ✅）")
    lines.append("```\n")

    lines.append("## 📷 发布选图顺序（在抖音按此顺序添加图片，首图设为封面）\n")
    if imgs:
        for i, name in enumerate(imgs, 1):
            tag = "  ← 设为封面" if i == 1 else ""
            lines.append(f"{i}. `{name}`{tag}")
    else:
        lines.append("（未检测到截图，请先运行 _screenshot_custom_html.py）")
    lines.append("")

    md = "\n".join(lines)
    os.makedirs(SHOTS, exist_ok=True)
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"saved {OUT_MD}")
    print(f"images found: {len(imgs)}")
    return md


if __name__ == "__main__":
    ds = datetime.date.today().strftime("%Y-%m-%d")
    build(ds)
