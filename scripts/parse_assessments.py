import json
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# ================= CONFIG =================
INPUT_LINKS = "data/raw/catalog_links.json"
OUTPUT_FILE = "data/processed/assessments.jsonl"

TEST_TYPE_MAP = {
    "A": "Ability & Aptitude",
    "B": "Biodata & Situational Judgement",
    "C": "Competencies",
    "D": "Development & 360",
    "E": "Assessment Exercises",
    "K": "Knowledge & Skills",
    "P": "Personality & Behavior",
    "S": "Simulations"
}

# ================= HELPERS =================
def safe_text(page, selector):
    try:
        el = page.query_selector(selector)
        return el.inner_text().strip() if el else ""
    except:
        return ""

def extract_name(page):
    """
    SHL pages do not consistently use <h1>.
    Try multiple robust selectors.
    """
    selectors = [
        "h1",
        "h2",
        "div.product-title",
        "div.page-title",
        "title"
    ]

    for sel in selectors:
        text = safe_text(page, sel)
        if text:
            return text.replace("| SHL", "").strip()

    return ""

def extract_description(page):
    try:
        locator = page.locator("text=Description").first
        if locator:
            parent = locator.evaluate_handle("el => el.parentElement")
            text = parent.inner_text()
            return text.replace("Description", "").strip()
    except:
        pass
    return ""

def extract_duration(page):
    body = page.inner_text("body")
    for line in body.splitlines():
        if "Approximate Completion Time" in line:
            digits = "".join(c for c in line if c.isdigit())
            return int(digits) if digits else 0
    return 0

def extract_test_types(page):
    """
    SHL uses single-letter Test Type codes (A, B, C, K, P, S, etc.)
    These letters appear in the HTML, not the full names.
    """
    body = page.inner_text("body")
    detected = []

    for code, label in TEST_TYPE_MAP.items():
        if f"\n{code}\n" in body or f" {code} " in body:
            detected.append(label)

    return detected

def is_blocked_page(page):
    body = page.inner_text("body").lower()
    return any(
        phrase in body
        for phrase in [
            "access denied",
            "forbidden",
            "error 403",
            "you do not have permission"
        ]
    )

# ================= MAIN =================
def main():
    Path("data/processed").mkdir(parents=True, exist_ok=True)

    with open(INPUT_LINKS, "r", encoding="utf-8") as f:
        urls = json.load(f)

    written = 0
    skipped = 0

    with sync_playwright() as p, open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        for idx, url in enumerate(urls, 1):
            print(f"[{idx}/{len(urls)}] Parsing {url}")

            try:
                page.goto(url, timeout=60000)
                page.wait_for_timeout(2000)

                if is_blocked_page(page):
                    skipped += 1
                    continue

                name = extract_name(page)
                if not name:
                    skipped += 1
                    continue

                description = extract_description(page)
                duration = extract_duration(page)
                test_types = extract_test_types(page)

                record = {
                    "url": url,
                    "name": name,
                    "description": description,
                    "duration": duration,
                    "remote_support": "Yes" if "Remote Testing" in page.content() else "No",
                    "adaptive_support": "Yes" if "Adaptive" in page.content() else "No",
                    "test_type": test_types,
                    "search_text": f"{name}. {description}. {' '.join(test_types)}"
                }

                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                written += 1

            except PlaywrightTimeout:
                skipped += 1
            except Exception as e:
                skipped += 1

        browser.close()

    print("\n==============================")
    print(f"✅ Records written: {written}")
    print(f"⛔ Pages skipped: {skipped}")
    print(f"📄 Output: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
