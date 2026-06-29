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
    print("[update] Starting diagnostic...", flush=True)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox",
                      "--disable-dev-shm-usage",
                      "--disable-blink-features=AutomationControlled"]
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

            page.goto("https://www.tradingview.com/accounts/signin/")
            page.wait_for_load_state("networkidle")
            time.sleep(3)

            # Click Email button
            page.click('button:has-text("Email")', timeout=10000)
            print("[update] Clicked Email button.", flush=True)
            time.sleep(3)

            # Log everything on the page after clicking Email
            inputs = page.query_selector_all("input")
            print(f"[debug] Found {len(inputs)} inputs after Email click", flush=True)
            for i, inp in enumerate(inputs[:10]):
                try:
                    itype  = inp.get_attribute("type") or ""
                    iname  = inp.get_attribute("name") or ""
                    iid    = inp.get_attribute("id") or ""
                    iauto  = inp.get_attribute("autocomplete") or ""
                    iplace = inp.get_attribute("placeholder") or ""
                    print(f"[debug] Input {i}: type='{itype}' name='{iname}' id='{iid}' autocomplete='{iauto}' placeholder='{iplace}'", flush=True)
                except Exception:
                    pass

            raise Exception("Diagnostic complete — check Railway logs")

    except Exception as e:
        print(f"[update] ERROR: {e}", flush=True)
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
