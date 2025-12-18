import sys
import os

# Add project root to PYTHONPATH
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
from app.recommender import SHLRecommender

K = 10

def recall_at_k(predicted, relevant, k=10):
    predicted = predicted[:k]
    if not relevant:
        return 0.0
    return len(set(predicted) & set(relevant)) / len(relevant)

def main():
    recommender = SHLRecommender()

    train_path = "data/train.csv"
    if not os.path.exists(train_path):
        raise FileNotFoundError("Train CSV not found. Ensure train.csv exists in data/")

    df = pd.read_csv(train_path)

    recalls = []

    for query, group in df.groupby("Query"):
        relevant = group["Assessment_url"].tolist()
        results = recommender.recommend(query, top_k=K)
        predicted = [r["url"] for r in results]

        r = recall_at_k(predicted, relevant, K)
        recalls.append(r)

        print(f"Query: {query[:60]}...")
        print(f"Recall@{K}: {r:.2f}\n")

    mean_recall = sum(recalls) / len(recalls)
    print("=" * 50)
    print(f"Mean Recall@{K}: {mean_recall:.4f}")

if __name__ == "__main__":
    main()
