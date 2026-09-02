from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Ensure the root directory is in sys.path so we can import agent.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import agent

app = FastAPI(title="Student Academic Advisor API")

from fastapi.staticfiles import StaticFiles

# Allow CORS for local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for the frontend
app.mount("/public", StaticFiles(directory="public"), name="public")

from fastapi.responses import RedirectResponse

@app.get("/")
def read_root():
    return RedirectResponse(url="/public/index.html")

class RecommendationRequest(BaseModel):
    completed_courses: List[str]
    interests: str
    top_n: int = 3

@app.get("/api/courses")
def get_courses():
    """Returns all available courses for the frontend dropdown."""
    courses = agent.load_courses()
    return {"courses": courses}

@app.post("/api/recommend")
def get_recommendations(req: RecommendationRequest):
    """Generates recommendations based on the user profile."""
    if not req.interests.strip():
        raise HTTPException(status_code=400, detail="Interests cannot be empty")
        
    results = agent.recommend_electives(
        completed_courses=req.completed_courses,
        interests=req.interests,
        top_n=req.top_n
    )
    
    if "error" in results:
        raise HTTPException(status_code=500, detail=results["error"])
        
    return results
