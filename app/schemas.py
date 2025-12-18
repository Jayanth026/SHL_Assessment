from pydantic import BaseModel
from typing import List

class HealthResponse(BaseModel):
    status: str

class RecommendRequest(BaseModel):
    query: str

class Assessment(BaseModel):
    url: str
    name: str
    adaptive_support: str
    description: str
    duration: int
    remote_support: str
    test_type: List[str]

class RecommendResponse(BaseModel):
    recommended_assessments: List[Assessment]
