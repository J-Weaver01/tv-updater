from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import os
import time

app = Flask(__name__)

TV_EMAIL    = os.environ["TV_EMAIL"]
TV_PASSWORD = os.environ["TV_PASSWORD"]
CHART_URL   = os.environ["CHART_URL"]

@app.route("/update", methods=["POST"])
def update():
    data     = request.json
    ticker_1 = data.get("ticker_1", "")
    ticker_2 = data.get("ticker_2", "")
    ticker_3 = data.get("ticker_3", "")
    ticker_4 = data.get("ticker_4", "")
    ticker_5 = data.get("ticker_5", "")
    ticker_6 = data.get("ticker_6", "")

    tickers = [ticker_1, ticker_2, ticker_3, ticker_4, ticker_5, ticker_6]
    print(f"[update] Received tickers: {tickers}", flush=True)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled"
                ]
            )
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                locale="en-US"
            )
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """)
            page = context.new_page()

            # ── LOGIN ──────────────────────────────────────────
            print("[update] Navigating to TradingView login...", flush=True)
            page.goto("https://www.tradingview.com/accounts/signin/")
            page.wait_for_load_state("networkidle")
            time.sleep(3)

            # Click Email button
            page.click('button:has-text("Email")', timeout=10000)
            time.sleep(2)
            print("[update] Clicked Email button.", flush=True)

            # Fill login form
            page.wait_for_selector('input[name="id_username"]', timeout=15000)
            page.fill('input[name="id_username"]', TV_EMAIL)
            page.fill('input[name="id_password"]', TV_PASSWORD)
            page.click('button[type="submit"]')
            page.wait_for_load_state("networkidle")
            time.sleep(5)
            print("[update] Logged in.", flush=True)

            # ── OPEN CHART ─────────────────────────────────────
            print(f"[update] Loading chart: {CHART_URL}", flush=True)
            page.goto(CHART_URL)
            page.wait_for_load_state("networkidle")
            time.sleep(6)
            print("[update] Chart loaded.", flush=True)

            # ── OPEN INDICATOR SETTINGS ────────────────────────
            legend = page.locator('div[data-name="legend-source-title"]').first
            legend.dblclick()
            page.wait_for_selector(
                'div[data-name="indicator-properties-dialog"]',
                timeout=12000
            )
            time.sleep(1)
            print("[update] Settings dialog open.", flush=True)

            # ── FILL THE 6 TICKER FIELDS ───────────────────────
            inputs = page.query_selector_all(
                'div[data-name="indicator-properties-dialog"] input[type="text"]'
            )
            print(f"[update] Found {len(inputs)} text inputs.", flush=True)

            for i, ticker in enumerate(tickers):
                if i < len(inputs):
                    inputs[i].triple_click()
                    inputs[i].fill(ticker)
                    time.sleep(0.3)
                    print(f"[update] Set slot {i+1} = {ticker}", flush=True)

            # ── SAVE ───────────────────────────────────────────
            page.click('button[name="submit"]')
            time.sleep(2)
            print("[update] Saved. Done.", flush=True)

            browser.close()

        return jsonify({"status": "success", "tickers": tickers}), 200

    except Exception as e:
        print(f"[update] ERROR: {e}", flush=True)
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
