#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将本地生成的 热搜_html/index.html 截图为 PNG：
- 封面：手机首屏（appbar + cover）
- 各平台卡片：每个 .card 元素单独截图
"""
import http.server, os, socketserver, threading, time
from playwright.sync_api import sync_playwright

ROOT = "/Users/yin/WorkBuddy/热搜小程序/热搜_html"
OUT = "/Users/yin/WorkBuddy/热搜小程序/热搜_html_shots"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT = 8150

os.makedirs(OUT, exist_ok=True)

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)
    def log_message(self, *args): pass

def serve():
    with socketserver.TCPServer(("127.0.0.1", PORT), H) as s:
        s.serve_forever()

threading.Thread(target=serve, daemon=True).start()
time.sleep(1)

with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path=CHROME,
        args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
    )
    page = browser.new_page(viewport={"width": 430, "height": 932}, device_scale_factor=2)
    page.goto(f"http://127.0.0.1:{PORT}/index.html", wait_until="networkidle", timeout=30000)
    time.sleep(2)

    # 封面：首屏视口（序号 0）
    cover_path = os.path.join(OUT, "0-cover.png")
    page.screenshot(path=cover_path)
    print(f"saved {cover_path}")

    # 各平台卡片（序号 1..N，与页面展示顺序一致）
    cards = page.query_selector_all(".card")
    print(f"found {len(cards)} cards")
    for i, card in enumerate(cards):
        try:
            name_el = card.query_selector(".nm")
            name = (name_el.inner_text() if name_el else f"card{i}").strip()
            # 生成安全文件名
            safe = name.replace(" ", "").replace("/", "_")
            page.evaluate("el => el.scrollIntoView({block:'center'})", card)
            time.sleep(0.5)
            path = os.path.join(OUT, f"{i+1}-{safe}.png")
            card.screenshot(path=path)
            print(f"saved {path} ({name})")
        except Exception as e:
            print(f"card {i} error: {e}")

    browser.close()

print("ALL:", sorted(os.listdir(OUT)))
