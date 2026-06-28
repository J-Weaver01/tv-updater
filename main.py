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
                java_script_enabled=True,
                locale="en-US"
            )

            # Hide webdriver flag
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            page = context.new_page()

            # ── LOGIN ──────────────────────────────────────────
            print("[update] Navigating to TradingView login...", flush=True)
            page.goto("https://www.tradingview.com/accounts/signin/")
            page.wait_for_load_state("networkidle")
            time.sleep(5)

            print(f"[debug] Page URL: {page.url}", flush=True)
            print(f"[debug] Page title: {page.title()}", flush=True)

            # Log all buttons to find the right selector
            buttons = page.query_selector_all("button")
            print(f"[debug] Found {len(buttons)} buttons", flush=True)
            for i, btn in enumerate(buttons[:15]):
                try:
                    text      = btn.inner_text().strip().replace("\n", " ")
                    data_name = btn.get_attribute("data-name") or ""
                    class_    = btn.get_attribute("class") or ""
                    print(f"[debug] Button {i}: text='{text}' data-name='{data_name}' class='{class_[:60]}'", flush=True)
                except Exception:
                    pass

            # Log all inputs
            inputs = page.query_selector_all("input")
            print(f"[debug] Found {len(inputs)} inputs", flush=True)
            for i, inp in enumerate(inputs[:10]):
                try:
                    itype = inp.get_attribute("type") or ""
                    iname = inp.get_attribute("name") or ""
                    print(f"[debug] Input {i}: type='{itype}' name='{iname}'", flush=True)
                except Exception:
                    pass

            raise Exception("Diagnostic run complete — check Railway logs for button and input details")

    except Exception as e:
        print(f"[update] ERROR: {e}", flush=True)
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
