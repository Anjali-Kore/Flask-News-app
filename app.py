from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get the News API key from environment variables
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

# Base URL for NewsAPI
NEWS_API_URL = 'https://newsapi.org/v2/everything'  # Changed from 'top-headlines' to 'everything'

@app.route('/', methods=['GET'])
def index():
    query = request.args.get('q')  # Get the search query from the URL
    news = fetch_news(query=query)
    articles = news.get('articles', [])
    status = news.get('status')
    message = news.get('message', '')
    
    print(f"Search Query: {query}")
    print(f"API Status: {status}")
    print(f"Number of Articles Fetched: {len(articles)}")
    
    if status != 'ok':
        # Pass an error message to the template if needed
        return render_template('index.html', articles=[], query=query, error=message)
    
    # Log sample articles
    for idx, article in enumerate(articles[:3], start=1):
        print(f"Article {idx}: {article.get('title')}")
    
    # Filter out articles missing essential fields
    filtered_articles = [article for article in articles if is_article_valid(article)]
    
    print(f"Number of Articles After Filtering: {len(filtered_articles)}")
    
    return render_template('index.html', articles=filtered_articles, query=query)

def fetch_news(query=None):
    params = {
        'apiKey': NEWS_API_KEY,
        'pageSize': 20,    # Number of articles to fetch
        'language': 'en',  # Language of the articles
        'sortBy': 'publishedAt',  # Sort articles by publication date
    }
    if query:
        params['q'] = query
    else:
        params['q'] = 'news'  # Default query to ensure articles are fetched

    try:
        response = requests.get(NEWS_API_URL, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return {'articles': [], 'status': 'error', 'message': str(e)}

def is_article_valid(article):
    """
    Check if the article contains all essential fields.
    """
    essential_fields = ['title', 'url', 'source', 'publishedAt']
    
    # 'description' and 'urlToImage' are optional
    
    # Check if all essential fields are present and non-empty
    for field in essential_fields:
        if field not in article or not article[field]:
            return False
    
    # Additionally, check if 'source' has 'name'
    if 'source' not in article or 'name' not in article['source'] or not article['source']['name']:
        return False
    
    return True

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%B %d, %Y %I:%M %p'):
    """
    Format the datetime string from the API to a more readable format.
    """
    try:
        dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime(format)
    except:
        return value  # Return as-is if parsing fails

if __name__ == '__main__':
    app.run(debug=True)
