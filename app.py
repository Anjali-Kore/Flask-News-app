from flask import Flask, render_template, request
import requests#to make requests to NewsApi
import os#
from dotenv import load_dotenv#
from datetime import datetime
import logging

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)#

NEWS_API_KEY = os.getenv('API_KEY')
NEWS_API_URL = 'https://newsapi.org/v2/everything'#url of newsapi where all the news data is stored

@app.route('/', methods=['GET'])
def index():
    query = request.args.get('q')#takes the query parameter from url eg http://localhost:5000/?q=technology q=technology 
    news = fetch_news(query=query)#uses that query to fetch articles
    articles = news.get('articles', [])
    status = news.get('status')
    message = news.get('message', '')

    if status != 'ok':
        return render_template('index.html', articles=[], query=query, error=message)

    filtered_articles = [article for article in articles if is_article_valid(article)]
    return render_template('index.html', articles=filtered_articles, query=query)

success_count = 0 
failure_count = 0

def fetch_news(query=None):
    global success_count, failure_count
    params = {
        'apiKey': NEWS_API_KEY,
        'pageSize': 20,
        'language': 'en',
        'sortBy': 'publishedAt',
    }
    if query:
        params['q'] = query# if query is provided provide query specific news
    else:
        params['q'] = 'news' #if query is not provided provide gneral news

    try:
        response = requests.get(NEWS_API_URL, params=params)
        response.raise_for_status()
        data = response.json()#converts json to dictionary
        success_count += 1
        logging.info(f"API call successful: {response.status_code} for query '{query}'")
        return data
    except requests.exceptions.RequestException as e:
        failure_count += 1
        logging.error(f"Error fetching news: {e} for query '{query}'")
        return {'articles': [], 'status': 'error', 'message': str(e)}

def get_success_rate():
    total_calls = success_count + failure_count
    if total_calls > 0:
        return (success_count / total_calls) * 100
    return 0

@app.route('/api_performance', methods=['GET'])
def api_performance():
    logging.info("API performance endpoint was hit")
    success_rate = get_success_rate()
    return f"API Success Rate: {success_rate:.2f}%"

def is_article_valid(article):
    essential_fields = ['title', 'url', 'source', 'publishedAt']
    for field in essential_fields:
        if field not in article or not article[field]:
            return False
    return True

@app.template_filter('datetimeformat')
def datetimeformat(value, format='%B %d, %Y %I:%M %p'):
    try:
        dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime(format)
    except:
        return value

if __name__ == '__main__':
    app.run(debug=True)
