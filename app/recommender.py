import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict


# ===============================
# Utility loaders
# ===============================

def load_meta(meta_path="data/index/meta.jsonl") -> List[Dict]:
    meta = []
    with open(meta_path, "r", encoding="utf-8") as f:
        for line in f:
            meta.append(json.loads(line))
    return meta


def load_full_catalog(path="data/processed/assessments.jsonl") -> Dict[str, Dict]:
    """
    Load full parsed SHL catalog.
    Keyed by URL for fast enrichment lookup.
    """
    catalog = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            catalog[record["url"]] = record
    return catalog


# ===============================
# Recommender Class
# ===============================

class SHLRecommender:
    def __init__(
        self,
        index_path="data/index/faiss.index",
        meta_path="data/index/meta.jsonl",
        catalog_path="data/processed/assessments.jsonl",
        model_name="sentence-transformers/all-mpnet-base-v2",
        top_k=10
    ):
        self.top_k = top_k

        # Load embedding model
        self.model = SentenceTransformer(model_name)

        # Load FAISS index
        self.index = faiss.read_index(index_path)

        # Load metadata & full catalog
        self.meta = load_meta(meta_path)
        self.full_catalog = load_full_catalog(catalog_path)

    # ===============================
    # Core Recommendation Logic
    # ===============================

    def recommend(self, query: str) -> List[Dict]:
        """
        1. Encode query
        2. FAISS search
        3. Enrich with full catalog
        4. Return API-ready records
        """

        # Encode query
        query_vec = self.model.encode([query]).astype("float32")

        # FAISS search
        scores, indices = self.index.search(query_vec, self.top_k)

        results = []
        seen_urls = set()

        for idx in indices[0]:
            if idx < 0 or idx >= len(self.meta):
                continue

            meta_rec = self.meta[idx]
            url = meta_rec["url"]

            # Avoid duplicates
            if url in seen_urls:
                continue
            seen_urls.add(url)

            # Enrich from full catalog
            full = self.full_catalog.get(url, {})

            results.append({
                "url": url,
                "name": full.get("name", meta_rec.get("name", "")),
                "adaptive_support": full.get("adaptive_support", "No"),
                "description": full.get("description", ""),
                "duration": full.get("duration", 0),
                "remote_support": full.get("remote_support", "No"),
                "test_type": full.get("test_type", [])
            })

        return results
