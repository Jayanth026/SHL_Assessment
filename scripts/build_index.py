import json
import os
import requests
from bs4 import BeautifulSoup
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from time import sleep

# ---------------- Paths ----------------
RAW_LINKS = "data/raw/catalog_links.json"
PROCESSED_DIR = "data/processed"
INDEX_DIR = "data/index"

ASSESSMENTS_JSONL = os.path.join(PROCESSED_DIR, "assessments.jsonl")
META_JSONL = os.path.join(INDEX_DIR, "meta.jsonl")
FAISS_INDEX_PATH = os.path.join(INDEX_DIR, "faiss.index")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

TEST_TYPE_MAP = {
    "A": "Ability & Aptitude",
    "B": "Biodata & Situational Judgement",
    "C": "Competencies",
    "D": "Development & 360",
    "E": "Assessment Exercises",
    "K": "Knowledge & Skills",
    "P": "Personality & Behavior",
    "S": "Simulations",
}

# ---------------- Helpers ----------------
def clean(text):
    return " ".join(text.split()) if text else ""

def parse_duration(text):
    # Extract minutes if present
    import re
    m = re.search(r"(\d+)\s*minute", text.lower())
    return int(m.group(1)) if m else 0

def parse_test_types(text):
    import re
    m = re.search(r"Test Type\s*:\s*([A-Z,\s]+)", text)
    if not m:
        return []
    letters = re.findall(r"[A-Z]", m.group(1))
    return list({TEST_TYPE_MAP[l] for l in letters if l in TEST_TYPE_MAP})

# ---------------- Parse Assessment Page ----------------
def parse_assessment(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    full_text = clean(soup.get_text(" "))

    name = clean(soup.find("h1").get_text()) if soup.find("h1") else ""
    description = ""
    for h in soup.find_all(["h2", "h3"]):
        if clean(h.get_text()).lower() == "description":
            description = clean(h.find_next().get_text())
            break

    duration = parse_duration(full_text)
    test_types = parse_test_types(full_text)

    remote_support = "Yes" if "Remote Testing" in full_text else "No"
    adaptive_support = "Yes" if "Adaptive" in full_text or "IRT" in full_text else "No"

    search_text = f"{name}. {description}. {' '.join(test_types)}"

    return {
        "url": url,
        "name": name,
        "description": description,
        "duration": duration,
        "remote_support": remote_support,
        "adaptive_support": adaptive_support,
        "test_type": test_types,
        "search_text": search_text
    }

# ---------------- Main ----------------
def main():
    if not os.path.exists(RAW_LINKS):
        raise FileNotFoundError(f"Missing {RAW_LINKS}. Run crawl_catalog.py first.")

    with open(RAW_LINKS, "r", encoding="utf-8") as f:
        urls = json.load(f)

    print(f"Parsing {len(urls)} assessment pages...")

    records = []
    for i, url in enumerate(urls, 1):
        try:
            rec = parse_assessment(url)
            records.append(rec)
            print(f"[{i}/{len(urls)}] Parsed")
            sleep(0.3)
        except Exception as e:
            print(f"[WARN] Failed {url}: {e}")

    # Save parsed data
    with open(ASSESSMENTS_JSONL, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"✅ Saved {len(records)} assessments to {ASSESSMENTS_JSONL}")

    # ---------------- Build FAISS ----------------
    embedder = SentenceTransformer("all-mpnet-base-v2")
    texts = [r["search_text"] for r in records]
    X = embedder.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    X = np.asarray(X, dtype="float32")

    index = faiss.IndexFlatIP(X.shape[1])
    index.add(X)
    faiss.write_index(index, FAISS_INDEX_PATH)

    with open(META_JSONL, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"✅ FAISS index saved to {FAISS_INDEX_PATH}")
    print(f"✅ Metadata saved to {META_JSONL}")

if __name__ == "__main__":
    main()
