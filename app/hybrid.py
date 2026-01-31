import pandas as pd

class HybridRecommender:
    def __init__(self, content_recommender, collaborative_recommender):
        self.content_recommender = content_recommender
        self.collaborative_recommender = collaborative_recommender

    
    def recommend(self, title, top_n=10):
        # 1. Resolve Title
        resolved_title = self.find_closest_title(title)
        if not resolved_title:
             return []
             
        # 2. Get Content Recommendations
        content_recs = self.content_recommender.get_recommendations(resolved_title, top_n=top_n)
        
        # 3. Get Collaborative Recommendations
        collab_recs = self.collaborative_recommender.get_recommendations(resolved_title, top_n=top_n)
        
        # 4. Handle Empty Content Results
        if isinstance(content_recs, list) and not content_recs:
             # If content based failed (shouldn't if title resolved), return empty
             return []
             
        # Fix DataFrames
        if isinstance(content_recs, list):
             # Should be DataFrame if not empty, but safety check
             content_recs = pd.DataFrame(content_recs)

        # 5. Handle Collaborative Results
        has_collab = False
        if isinstance(collab_recs, pd.DataFrame):
            if not collab_recs.empty:
                has_collab = True
        elif isinstance(collab_recs, list) and len(collab_recs) > 0:
             has_collab = True
             collab_recs = pd.DataFrame(collab_recs)
             
        if not has_collab:
             print("No collaborative data found. Returning content-based results.")
             return content_recs.head(top_n).to_dict('records')

        # 6. Combine Results
        content_recs = content_recs.copy()
        content_recs['source'] = 'content'
        
        collab_recs = collab_recs.copy()
        collab_recs['source'] = 'collaborative'
        
        # --- Weighted Hybrid Logic ---
        # Weights: Content-Based gets higher priority to ensure "Thor" matches "Thor: ..."
        # because Content-Based checks Title Similarity now.
        w_content = 0.6
        w_collab = 0.4
        
        content_recs['weighted_score'] = content_recs['score'] * w_content
        collab_recs['weighted_score'] = collab_recs['score'] * w_collab
        
        combined = pd.concat([content_recs, collab_recs])
        
        # Sum scores for duplicates to boost movies that appear in both
        # We group by movieId to ensure uniqueness
        combined_grouped = combined.groupby(['movieId', 'title', 'genres'])['weighted_score'].sum().reset_index()
        
        # Add a raw score for debugging/thresholding?
        # Actually, weighted_score is enough.
        
        # Sort by final score
        final_recs = combined_grouped.sort_values(by='weighted_score', ascending=False)
        
        # --- Thresholding ---
        # Filter unlikely matches. 
        # Content score for "Thor" <-> "Harry Potter" (only genre match) might be around 0.1-0.2.
        # "Thor" <-> "Thor: Ragnarok" (Title + Genre) will be > 0.4.
        # Let's set a conservative threshold.
        min_score_threshold = 0.10
        final_recs = final_recs[final_recs['weighted_score'] > min_score_threshold]
        
        # Remove the searched movie itself
        final_recs = final_recs[final_recs['title'] != resolved_title]
        
        # Rename weighted_score back to score for frontend consistency
        final_recs = final_recs.rename(columns={'weighted_score': 'score'})
        
        # Debug print
        print("Top 5 Hybrid Recommendations:")
        print(final_recs[['title', 'score']].head(5))
        
        return final_recs.head(top_n).to_dict('records')

    def find_closest_title(self, title):
        if hasattr(self.content_recommender, 'resolve_title'):
             return self.content_recommender.resolve_title(title)
        return title
