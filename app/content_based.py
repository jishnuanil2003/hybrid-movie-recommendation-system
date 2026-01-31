from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

class ContentRecommender:
    def __init__(self, movies_df):
        self.movies_df = movies_df
        self.tfidf_matrix = None
        self.indices = None
        self._prepare_data()

    def _prepare_data(self):
        # Clean genres (replace | with space)
        self.movies_df['genres_clean'] = self.movies_df['genres'].apply(lambda x: str(x).replace('|', ' '))
        
        # Create a "soup" of metadata (Title + Genres)
        # We verify that standardizing title helps with matching
        def clean_data(x):
            if isinstance(x, str):
                return str.lower(x.replace(":", "").replace("-", ""))
            else:
                return ""
                
        # Apply cleaning to title for the soup
        self.movies_df['title_clean'] = self.movies_df['title'].apply(clean_data)
        self.movies_df['soup'] = self.movies_df['title_clean'] + ' ' + self.movies_df['genres_clean'].str.lower()
        
        # Use TF-IDF on the soup
        # Using min_df=0 to ensure we capture all terms, or simple defaults
        tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = tfidf.fit_transform(self.movies_df['soup'])
        
        # Map movie titles to indices
        self.indices = pd.Series(self.movies_df.index, index=self.movies_df['title']).drop_duplicates()
        self.all_titles = self.movies_df['title'].tolist()

    def resolve_title(self, title):
        import difflib
        
        # 1. Exact match
        if title in self.indices:
            return title
            
        # 2. Case-insensitive exact match
        normalized_titles = self.movies_df['title'].str.lower()
        matches = self.movies_df[normalized_titles == title.lower()]
        if not matches.empty:
            return matches.iloc[0]['title']
        
        # 3. Fuzzy match
        close_matches = difflib.get_close_matches(title, self.all_titles, n=1, cutoff=0.6)
        if close_matches:
            return close_matches[0]
            
        # 4. Substring match (fallback)
        substring_matches = self.movies_df[self.movies_df['title'].str.contains(title, case=False, regex=False)]
        if not substring_matches.empty:
            best_match = substring_matches.loc[substring_matches['title'].str.len().idxmin()]
            return best_match['title']
            
        return None

    def get_recommendations(self, title, top_n=10):
        """Returns top_n similar movies based on content."""
        title = self.resolve_title(title)
        if not title:
            return []

        idx = self.indices[title]
        
        # Determine the resolved title index
        if isinstance(idx, pd.Series):
            idx = idx.iloc[0]
            
        print(f"Content-Based: Resolved '{title}' (ID: {idx})")

        # Compute cosine similarity
        cosine_sim = linear_kernel(self.tfidf_matrix[idx], self.tfidf_matrix)

        sim_scores = list(enumerate(cosine_sim[0]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        # Take top_n * 2 candidates to allow filtering, excluding self
        sim_scores = sim_scores[1:top_n*2+1]
        
        movie_indices = [i[0] for i in sim_scores]
        scores = [i[1] for i in sim_scores]
        
        results = self.movies_df.iloc[movie_indices].copy()
        results['score'] = scores
        
        # Filter weak matches (optional, but requested "True similarity")
        # If score is very low, it's just genre noise.
        # But let's let Hybrid handle the thresholding or keep it loose here.
        
        return results[['movieId', 'title', 'genres', 'score']]

import pandas as pd
