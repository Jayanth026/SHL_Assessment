import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
INDEX_DIR = os.path.join(DATA_DIR, "index")

ASSESSMENTS_JSONL = os.path.join(DATA_DIR, "assessments.jsonl")
META_JSONL = os.path.join(INDEX_DIR, "meta.jsonl")
FAISS_INDEX = os.path.join(INDEX_DIR, "faiss.index")
