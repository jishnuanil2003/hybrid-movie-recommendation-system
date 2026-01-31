## Hybrid Movie Recommendation System

This project is a web-based movie recommendation system that uses a **hybrid approach**
combining **Content-Based Filtering** and **Collaborative Filtering** to provide accurate
and relevant movie suggestions.

### How It Works
- **Content-Based Filtering:** Uses movie title and genres with TF-IDF and cosine similarity
  to recommend similar movies (e.g., *Thor → Thor: Ragnarok*).
- **Collaborative Filtering:** Uses MovieLens user ratings and item-based cosine similarity
  to recommend movies preferred by similar users.
- **Hybrid Logic:** Combines both results using weighted scoring for better accuracy.

### How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
2.	Download MovieLens dataset and place movies.csv and ratings.csv inside a data/ folder.
3.	Start the backend server:
       uvicorn app.main:app --reload
4.	Open static/index.html in a browser.

How to Use
	1.	Enter a movie name (e.g., Thor) in the search box.
	2.	Click Recommend.
	3.	The system displays similar and user-preferred movie recommendations.

The backend is built using FastAPI, and the frontend uses HTML, CSS, and JavaScript.
