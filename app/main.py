import os
from fastapi import FastAPI
from pydantic import BaseModel
from app.recommender import SHLRecommender

app = FastAPI()
recommender = SHLRecommender()

class QueryRequest(BaseModel):
    query: str

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/recommend")
def recommend(req: QueryRequest):
    return {
        "recommended_assessments": recommender.recommend(req.query)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )
