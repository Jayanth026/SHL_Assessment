from playwright.sync_api import sync_playwright, TimeoutError
from time import sleep
import json
import os

BASE_URL = "https://www.shl.com/products/product-catalog/"
OUT_DIR = os.path.join("data", "raw")
os.makedirs(OUT_DIR, exist_ok=True)

ITEMS_PER_PAGE = 12
MAX_PAGES = 50  # safe upper bound

def main():
    all_links = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,   # keep visible for stability
            slow_mo=30
        )
        page = browser.new_page()

        for page_idx in range(MAX_PAGES):
            start = page_idx * ITEMS_PER_PAGE
            url = f"{BASE_URL}?type=1&start={start}"

            print(f"Loading page {page_idx + 1} (start={start})")

            try:
                page.goto(url, wait_until="load", timeout=30000)
            except TimeoutError:
                print("  ⚠️ Timeout on page load — retrying once")
                try:
                    page.goto(url, wait_until="load", timeout=30000)
                except TimeoutError:
                    print("  ❌ Failed again, skipping this page")
                    continue

            # Give JS time to render cards
            sleep(2)

            links = page.eval_on_selector_all(
                "a[href*='product-catalog/view']",
                "els => els.map(e => e.href)"
            )

            print(f"  Found {len(links)} links")

            # Stop condition: no results
            if len(links) == 0:
                print("No more results, stopping crawl.")
                break

            for link in links:
                all_links.add(link)

        browser.close()

    all_links = sorted(all_links)

    out_path = os.path.join(OUT_DIR, "catalog_links.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_links, f, indent=2)

    print("\n==============================")
    print(f"✅ Total Individual Test Solutions: {len(all_links)}")
    print(f"📄 Saved to {out_path}")

    if len(all_links) >= 377:
        print("🎯 SHL requirement satisfied (≥377)")
    else:
        print("❌ Requirement NOT satisfied — increase MAX_PAGES")

if __name__ == "__main__":
    main()
