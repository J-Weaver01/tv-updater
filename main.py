from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import os
import time

app = Flask(__name__)

TV_EMAIL = os.environ["TV_EMAIL"]
TV_PASSWORD = os.environ["TV_PASSWORD"]
CHART_URL = os.environ["CHART_URL"]

@app.route("/update", methods=["POST"])
def update():
    data = request.json
    ticker_1 = data.get("ticker_1")
    ticker_2 = data.get("ticker_2")

    if not ticker_1 or not ticker_2:
        return jsonify({"error": "Missing tickers"}), 400

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            page.goto("https://www.tradingview.com/accounts/signin/")
            page.wait_for_load_state("networkidle")
            page.fill('input[name="username"]', TV_EMAIL)
            page.fill('input[name="password"]', TV_PASSWORD)
            page.click('button[type="submit"]')
            page.wait_for_load_state("networkidle")
            time.sleep(3)

            page.goto(CHART_URL)
            page.wait_for_load_state("networkidle")
            time.sleep(5)

            browser.close()

        return jsonify({
            "status": "success",
            "ticker_1": ticker_1,
            "ticker_2": ticker_2
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
