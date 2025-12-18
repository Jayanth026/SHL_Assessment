from fastapi import FastAPI
from .schemas import *
from .recommender import SHLRecommender
from .jd_fetcher import is_url, fetch_jd_text

app = FastAPI()
model = SHLRecommender()

@app.get("/health", response_model=HealthResponse)
def health():
    return {"status": "healthy"}

@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    q = fetch_jd_text(req.query) if is_url(req.query) else req.query
    recs = model.recommend(q)
    return {"recommended_assessments": recs}
