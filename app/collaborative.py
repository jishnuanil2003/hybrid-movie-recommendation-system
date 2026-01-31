import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.impute import SimpleImputer
import numpy as np

class CollaborativeRecommender:
    def __init__(self, ratings_df, movies_df):
        self.ratings_df = ratings_df
        self.movies_df = movies_df
        self.user_movie_matrix = None
        self.item_similarity_df = None
        self._prepare_data()

    def _prepare_data(self):
        # Create User-Movie Matrix
        # Rows: Users, Cols: Movies
        self.user_movie_matrix = self.ratings_df.pivot_table(
            index='userId', 
            columns='movieId', 
            values='rating'
        )
        
        # Fill NaN with 0 for sparsity handling (simplest approach for cosine sim)
        # Alternatively, centered cosine (substract mean). 
        # For simplicity and standard Item-Based CF, 0 fill is common or using sparse matrices.
        self.user_movie_matrix_filled = self.user_movie_matrix.fillna(0)
        
        # Compute Item-Item Similarity
        # Transpose to get Movie-User matrix for calculating similarity between Movies
        movie_user_matrix = self.user_movie_matrix_filled.T
        
        # Calculate Cosine Similarity between items (movies)
        # Result is a square matrix (n_movies x n_movies)
        self.item_similarity = cosine_similarity(movie_user_matrix)
        
        # Convert to DataFrame for easier lookup
        self.item_similarity_df = pd.DataFrame(
            self.item_similarity,
            index=movie_user_matrix.index,
            columns=movie_user_matrix.index
        )

    def get_recommendations(self, movie_title, top_n=10):
        # Find movieId for the title
        movie_matches = self.movies_df[self.movies_df['title'] == movie_title]
        if movie_matches.empty:
            return []
            
        movie_id = movie_matches.iloc[0]['movieId']
        
        if movie_id not in self.item_similarity_df.index:
            return []
            
        # Get similarity scores for this movie
        sim_scores = self.item_similarity_df[movie_id]
        
        # Sort values
        sim_scores = sim_scores.sort_values(ascending=False)
        
        # Drop self
        sim_scores = sim_scores.drop(movie_id)
        
        # Get top N
        top_scores = sim_scores.head(top_n)
        
        # Get Movie Details
        results = []
        for mid, score in top_scores.items():
            movie_info = self.movies_df[self.movies_df['movieId'] == mid].iloc[0]
            results.append({
                'movieId': mid,
                'title': movie_info['title'],
                'genres': movie_info['genres'],
                'score': score
            })
            
        return pd.DataFrame(results)
