import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

PRODUCT_URL = "https://www.amazon.com/dp/B0FHC2P7NB"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def download_product_page() -> None:
    try:
        response = requests.get(
            PRODUCT_URL,
            headers=HEADERS,
            timeout=15,
        )

        print(f"Status code: {response.status_code}")
        print(f"Response length: {len(response.text)} characters")
        print(f"Final URL: {response.url}")

        soup = BeautifulSoup(response.text, "html.parser")

        # Temporary: always save the full page for diagnosis
        with open("debug_response.html", "w", encoding="utf-8") as file:
            file.write(response.text)
        print("Saved full response to debug_response.html for inspection")

        # 1. Check for CAPTCHA
        challenge = soup.select_one('form[action="/errors_page/validateCaptcha"]')
        if challenge:
            print("Amazon challenge detected. Product page was not returned.")
            status = "CAPTCHA"
        else:
            # 2. Try to get the price
            price_element = soup.select_one("#apex-pricetopay-accessibility-label")
            if price_element:
                status = price_element.get_text(strip=True)
                print(f"Price: {status}")
            else:
                status = "Price not found"
                print("Price not found")


        # Always write one row
        with open("price_history.csv", "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now().isoformat(), status])

    except requests.RequestException as error:
        print(f"Request failed: {error}")
        # Even on network error we can record it
        with open("price_history.csv", "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now().isoformat(), f"Request failed: {error}"])


download_product_page()