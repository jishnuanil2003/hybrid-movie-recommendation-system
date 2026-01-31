import pandas as pd
import os

class DataLoader:
    def __init__(self, movies_path="data/movies.csv", ratings_path="data/ratings.csv"):
        self.movies_path = movies_path
        self.ratings_path = ratings_path
        self.movies_df = None
        self.ratings_df = None

    def load_data(self):
        """Loads movies and ratings data from CSV files."""
        if not os.path.exists(self.movies_path) or not os.path.exists(self.ratings_path):
            raise FileNotFoundError("Data files not found. Please run setup_data.py first.")
            
        self.movies_df = pd.read_csv(self.movies_path)
        self.ratings_df = pd.read_csv(self.ratings_path)
        
        # Initial preprocessing if needed (e.g., handling missing values in relevant columns)
        self.movies_df['genres'] = self.movies_df['genres'].fillna('')
        
        return self.movies_df, self.ratings_df

    def get_movies(self):
        if self.movies_df is None:
            self.load_data()
        return self.movies_df

    def get_ratings(self):
        if self.ratings_df is None:
            self.load_data()
        return self.ratings_df
