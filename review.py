import time
import os
import csv
import random
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

REVIEWS_URL = "https://www.amazon.in/product-reviews/B0F6V44NS7/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews"

CSV_FILE = "amazon_reviews.csv"
MEDIA_DIR = "review_media"

os.makedirs(MEDIA_DIR, exist_ok=True)

options = webdriver.ChromeOptions()
options.debugger_address = "127.0.0.1:9222"

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

driver.get(REVIEWS_URL)
time.sleep(3)

csv_file = open(CSV_FILE, "w", newline="", encoding="utf-8")
writer = csv.writer(csv_file)

writer.writerow([
    "review_id", "reviewer", "rating", "color", "size",
    "title", "text", "date", "images"
])

scraped_ids = set()

print("🚀 Scraping started...")

while True:
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-hook='review']")))
    reviews = driver.find_elements(By.CSS_SELECTOR, "[data-hook='review']")
    print(f"Found {len(reviews)} reviews")

    for r in reviews:
        review_id = r.get_attribute("id")
        if review_id in scraped_ids:
            continue
        scraped_ids.add(review_id)

        def safe_text(css):
            try:
                return r.find_element(By.CSS_SELECTOR, css).text.strip()
            except:
                return ""

        def safe_rating():
            try:
                return r.find_element(By.CSS_SELECTOR, "[data-hook='review-star-rating'] .a-icon-alt").text.strip()
            except:
                return ""

        def safe_format():
            try:
                return r.find_element(By.CSS_SELECTOR, "[data-hook='format-strip']").text.strip()
            except:
                return ""

        reviewer = safe_text(".a-profile-name")
        rating = safe_rating()
        title = safe_text("[data-hook='review-title']")
        text = safe_text("[data-hook='review-body']")
        date = safe_text("[data-hook='review-date']")

        format_info = safe_format()

        color = ""
        size = ""

        if "Colour" in format_info:
            try:
                parts = format_info.split("|")
                color = parts[0].replace("Colour:", "").strip()
                size = parts[1].replace("Size:", "").strip()
            except:
                pass

        image_urls = []
        try:
            imgs = r.find_elements(By.CSS_SELECTOR, "img[data-hook='review-image-tile']")
            image_urls = [img.get_attribute("src") for img in imgs if img.get_attribute("src")]
        except:
            pass

        writer.writerow([
            review_id, reviewer, rating, color, size,
            title, text, date, "|".join(image_urls)
        ])

        if image_urls:
            folder = os.path.join(MEDIA_DIR, review_id)
            os.makedirs(folder, exist_ok=True)
            for i, url in enumerate(image_urls):
                try:
                    with open(f"{folder}/img_{i}.jpg", "wb") as f:
                        f.write(requests.get(url, timeout=10).content)
                except:
                    pass

        time.sleep(random.uniform(1,2))

    try:
        next_btn = driver.find_element(By.CSS_SELECTOR, "li.a-last a")
        driver.execute_script("arguments[0].click();", next_btn)
        time.sleep(3)
    except:
        print("✅ All pages scraped")
        break

csv_file.close()
driver.quit()

print("🎉 Reviews saved successfully!")
