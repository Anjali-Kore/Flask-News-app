import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import joblib

def load_content_models():
    vectorizer = joblib.load('models/vectorizer.pkl')
    tfidf_matrix = joblib.load('models/tfidf_matrix.pkl')
    cosine_sim_matrix = joblib.load('models/cosine_sim_matrix.pkl')
    news_data_cleaned = pd.read_csv('data/news.tsv', sep='\t', header=None).dropna(subset=[3,4])
    news_data_cleaned['combined_text'] = news_data_cleaned[3] + " " + news_data_cleaned[4]
    news_data_cleaned = news_data_cleaned.dropna(subset=['combined_text'])
    return vectorizer, tfidf_matrix, cosine_sim_matrix, news_data_cleaned

def get_content_recommendations(user_id, interaction_df, news_data_cleaned, cosine_sim_matrix, news_id_to_index, N=10, search_query=None):
    user_history = interaction_df[interaction_df['user_id'] == user_id]
    valid_news_ids = set(news_data_cleaned[0].astype(str))
    user_history_filtered = user_history[user_history['news_id'].isin(valid_news_ids)]

    if user_history_filtered.empty and not search_query:
        return []

    if not user_history_filtered.empty:
        user_article_indices = [news_id_to_index[news_id] for news_id in user_history_filtered['news_id']]
        sim_scores = cosine_sim_matrix[user_article_indices].mean(axis=0)
    else:
        sim_scores = cosine_sim_matrix.mean(axis=0)  # Fallback if no history

    # If search_query is provided, boost similarity scores for articles matching the query
    if search_query:
        search_query = search_query.lower()
        match_indices = news_data_cleaned[
            news_data_cleaned[3].str.lower().str.contains(search_query) | 
            news_data_cleaned[4].str.lower().str.contains(search_query)
        ].index.tolist()
        sim_scores[match_indices] += 0.1  # Boost scores; adjust the value as needed

    top_article_indices = sim_scores.argsort()[-N:][::-1]
    recommended_articles = news_data_cleaned.iloc[top_article_indices][0].astype(str).tolist()
    return recommended_articles
