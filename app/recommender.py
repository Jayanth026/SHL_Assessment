# app/recommender.py

import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INDEX_PATH = BASE_DIR / "data/index/faiss.index"
META_PATH = BASE_DIR / "data/index/meta.jsonl"


class SHLRecommender:
    def __init__(self, top_k: int = 10):
        self.top_k = top_k
        self.model = None  # lazy load
        self.index = faiss.read_index(str(INDEX_PATH))
        self.metadata = self._load_metadata()

    def _load_model(self):
        if self.model is None:
            # Smaller + stable model (recommended for Render free tier)
            self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def _load_metadata(self):
        data = []
        with open(META_PATH, "r", encoding="utf-8") as f:
            for line in f:
                data.append(json.loads(line))
        return data

    def recommend(self, query: str):
        self._load_model()

        query_embedding = self.model.encode(
            query,
            normalize_embeddings=True
        ).astype("float32")

        scores, indices = self.index.search(
            np.array([query_embedding]),
            self.top_k
        )

        results = []
        for idx in indices[0]:
            if idx < len(self.metadata):
                item = self.metadata[idx]

                results.append({
                    "url": item.get("url", ""),
                    "name": item.get("name", ""),
                    "adaptive_support": item.get("adaptive_support", "No"),
                    "description": item.get("description", ""),
                    "duration": item.get("duration", 0),
                    "remote_support": item.get("remote_support", "No"),
                    "test_type": item.get("test_type", [])
                })

        return results
