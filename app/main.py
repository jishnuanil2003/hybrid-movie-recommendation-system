from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import os

from app.data_loader import DataLoader
from app.content_based import ContentRecommender
from app.collaborative import CollaborativeRecommender
from app.hybrid import HybridRecommender

app = FastAPI(title="Hybrid Movie Recommender API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to hold recommender instances
recommender = None

@app.on_event("startup")
def startup_event():
    global recommender
    print("Loading data and initializing recommenders...")
    
    # Initialize Data Loader
    data_loader = DataLoader()
    movies_df, ratings_df = data_loader.load_data()
    
    # Initialize Recommenders
    print("Training Content-Based Recommender...")
    content_rec = ContentRecommender(movies_df)
    
    print("Training Collaborative Recommender...")
    collab_rec = CollaborativeRecommender(ratings_df, movies_df)
    
    print("Initializing Hybrid Recommender...")
    recommender = HybridRecommender(content_rec, collab_rec)
    print("System ready!")

@app.get("/recommend")
async def get_recommendations(title: str = Query(..., description="Movie title to search for")):
    if recommender is None:
        raise HTTPException(status_code=503, detail="System is still initializing")
    
    try:
        print(f"Request: Recommend for '{title}'")
        recommendations = recommender.recommend(title)
        
        if not recommendations:
             print(f"No recommendations found for '{title}'")
             return JSONResponse(content={"message": f"No recommendations found for '{title}'. Try checking the spelling.", "data": []})
             
        print(f"Found {len(recommendations)} recommendations.")
        return JSONResponse(content={"message": "Success", "data": recommendations})
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve static files for frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")
