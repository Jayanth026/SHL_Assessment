import sys
import os
import json
import pandas as pd

# Add project root to PYTHONPATH
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from app.recommender import SHLRecommender

OUTPUT_PATH = "data/predictions.csv"
TOP_K = 10

def main():
    recommender = SHLRecommender()

    # Load Test-Set from Excel
    test_xlsx = "C:\\Users\\jayan\\Downloads\\shl-assessment-recommender\\data\\Gen_AI Dataset.xlsx"
    if not os.path.exists(test_xlsx):
        raise FileNotFoundError("Gen_AI Dataset.xlsx not found in project root")

    df = pd.read_excel(test_xlsx, sheet_name="Test-Set")

    predictions = []

    for _, row in df.iterrows():
        query = row["Query"]
        results = recommender.recommend(query, top_k=TOP_K)
        urls = [r["url"] for r in results]

        predictions.append({
            "query": query,
            "predictions": "|".join(urls)
        })

        print(f"Generated predictions for query: {query[:60]}...")

    # Save CSV in required format
    out_df = pd.DataFrame(predictions)
    out_df.to_csv(OUTPUT_PATH, index=False)

    print("=" * 50)
    print(f"✅ Predictions saved to {OUTPUT_PATH}")
    print(f"Rows: {len(out_df)}")

if __name__ == "__main__":
    main()
