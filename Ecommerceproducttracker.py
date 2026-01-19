import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SEARCH_URL = "https://www.amazon.in/s?k=amazon&i=electronics&crid=OVJ2WAY651EH&sprefix=amazo%2Celectronics%2C394&ref=nb_sb_noss_2"
CSV_FILE = "amazon_search_results.csv"

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

driver.get(SEARCH_URL)

# wait for products to load
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot")))

products = driver.find_elements(By.CSS_SELECTOR, "div.s-main-slot > div[data-asin]")

print(f"Found {len(products)} products on the page")

with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "asin", "title", "url", "price", "rating", "review_count"
    ])

    for p in products:
        asin = p.get_attribute("data-asin").strip()
        if not asin:
            continue

        # product URL
        try:
            link = p.find_element(By.CSS_SELECTOR, "h2 a")
            url = link.get_attribute("href")
            title = link.text.strip()
        except:
            url = ""
            title = ""

        # price
        try:
            price = p.find_element(By.CSS_SELECTOR, ".a-price .a-offscreen").text.strip()
        except:
            price = ""

        # rating
        try:
            rating = p.find_element(By.CSS_SELECTOR, "i.a-icon-star-small span").text.strip()
        except:
            rating = ""

        # review count
        try:
            review_count = p.find_element(By.CSS_SELECTOR, "div.a-row span.a-size-base").text.strip()
        except:
            review_count = ""

        writer.writerow([asin, title, url, price, rating, review_count])

        print(f"Scraped: {title[:40]}...")

driver.quit()
print("✅ Done! Saved to", CSV_FILE)
