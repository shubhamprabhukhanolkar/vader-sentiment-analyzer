from flask import Flask, render_template, request, jsonify
import praw
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
import configparser
import os
import re

app = Flask(__name__)

class RedditStockSentiment:
    def __init__(self, config_file='secrets.ini'):
        """Initialize Reddit API connection and VADER sentiment analyzer."""
        
        # Try to get credentials from environment variables first (for deployment)
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        user_agent = os.getenv('REDDIT_USER_AGENT')
        
        # If not in environment, read from secrets.ini (for local development)
        if not client_id or not client_secret or not user_agent:
            config = configparser.ConfigParser()
            if not os.path.exists(config_file):
                raise FileNotFoundError(f"{config_file} not found. Please create it or set environment variables.")
            
            config.read(config_file)
            
            try:
                client_id = config.get('REDDIT', 'CLIENT_ID')
                client_secret = config.get('REDDIT', 'CLIENT_SECRET')
                user_agent = config.get('REDDIT', 'USER_AGENT')
            except (configparser.NoSectionError, configparser.NoOptionError):
                client_id = config.get('reddit', 'client_id')
                client_secret = config.get('reddit', 'client_secret')
                user_agent = config.get('reddit', 'user_agent')
        
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.analyzer = SentimentIntensityAnalyzer()
    
    def preprocess_text(self, text):
        """Clean and preprocess text for sentiment analysis."""
        if not text or text.strip() == '':
            return ''
        
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        text = re.sub(r'r/\w+', '', text)
        text = re.sub(r'u/\w+', '', text)
        
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001F900-\U0001F9FF"
            u"\U0001FA00-\U0001FA6F"
            u"\U00002600-\U000026FF"
            u"\U00002700-\U000027BF"
            "]+", flags=re.UNICODE)
        text = emoji_pattern.sub(r'', text)
        text = re.sub(r'[^a-zA-Z0-9\s.,!?\'\-$%]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def get_stock_variations(self, stock_query):
        """Get different variations of stock query."""
        ticker_to_name = {
            'TSLA': 'Tesla', 'AAPL': 'Apple', 'GME': 'GameStop',
            'AMC': 'AMC', 'NVDA': 'Nvidia', 'MSFT': 'Microsoft',
            'GOOGL': 'Google', 'GOOG': 'Google', 'AMZN': 'Amazon',
            'META': 'Meta', 'NFLX': 'Netflix', 'AMD': 'AMD',
            'PLTR': 'Palantir', 'BB': 'BlackBerry', 'NOK': 'Nokia',
            'SPCE': 'Virgin Galactic', 'NIO': 'NIO', 'COIN': 'Coinbase',
        }
        
        query_upper = stock_query.upper()
        search_terms = [stock_query]
        
        if query_upper in ticker_to_name:
            search_terms.append(ticker_to_name[query_upper])
        else:
            for ticker, name in ticker_to_name.items():
                if name.lower() == stock_query.lower():
                    search_terms.append(ticker)
                    break
        
        return search_terms
    
    def search_posts(self, subreddit_name, stock_query, limit=5, sort='new'):
        """Search for posts in subreddit."""
        subreddit = self.reddit.subreddit(subreddit_name)
        posts = []
        seen_ids = set()
        
        search_terms = self.get_stock_variations(stock_query)
        
        for term in search_terms:
            search_params = {'limit': limit, 'sort': sort}
            if sort == 'top':
                search_params['time_filter'] = 'month'
            
            for submission in subreddit.search(term, **search_params):
                if submission.id not in seen_ids:
                    seen_ids.add(submission.id)
                    post_data = {
                        'title': submission.title,
                        'text': submission.selftext,
                        'score': submission.score,
                        'url': submission.url,
                        'created_utc': datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                        'num_comments': submission.num_comments,
                        'post_id': submission.id
                    }
                    posts.append(post_data)
                    if len(posts) >= limit:
                        break
            if len(posts) >= limit:
                break
        
        return posts[:limit]
    
    def analyze_sentiment(self, text):
        """Analyze sentiment using VADER."""
        scores = self.analyzer.polarity_scores(text)
        return scores
    
    def analyze_stock_sentiment(self, subreddit_name, stock_query):
        """Main function to analyze stock sentiment."""
        top_posts = self.search_posts(subreddit_name, stock_query, limit=5, sort='top')
        new_posts = self.search_posts(subreddit_name, stock_query, limit=5, sort='new')
        
        all_posts = top_posts + new_posts
        seen_ids = set()
        unique_posts = []
        for post in all_posts:
            if post['post_id'] not in seen_ids:
                seen_ids.add(post['post_id'])
                unique_posts.append(post)
        
        results = []
        for post in unique_posts:
            full_text = f"{post['title']} {post['text']}"
            cleaned_text = self.preprocess_text(full_text)
            
            if not cleaned_text:
                continue
            
            sentiment = self.analyze_sentiment(cleaned_text)
            
            result = {
                'timestamp': post['created_utc'],
                'post': cleaned_text[:300] + '...' if len(cleaned_text) > 300 else cleaned_text,
                'sentiment_score': round(sentiment['compound'], 3),
                'url': post['url']
            }
            results.append(result)
        
        return results

# Initialize the analyzer
analyzer = RedditStockSentiment()

# Predefined lists
STOCKS = [
    'TSLA', 'AAPL', 'GME', 'AMC', 'NVDA', 
    'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX',
    'AMD', 'PLTR', 'BB', 'NOK', 'NIO', 'COIN'
]

SUBREDDITS = [
    'wallstreetbets', 'stocks', 'investing', 
    'StockMarket', 'options', 'pennystocks',
    'Daytrading', 'SecurityAnalysis'
]

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html', stocks=STOCKS, subreddits=SUBREDDITS)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handle sentiment analysis request."""
    try:
        data = request.json
        stock = data.get('stock')
        subreddit = data.get('subreddit')
        
        if not stock or not subreddit:
            return jsonify({'error': 'Please select both stock and subreddit'}), 400
        
        results = analyzer.analyze_stock_sentiment(subreddit, stock)
        
        if not results:
            return jsonify({'error': 'No posts found for this stock'}), 404
        
        # Calculate summary statistics
        scores = [r['sentiment_score'] for r in results]
        summary = {
            'total_posts': len(results),
            'avg_sentiment': round(sum(scores) / len(scores), 3),
            'max_sentiment': round(max(scores), 3),
            'min_sentiment': round(min(scores), 3),
            'positive_posts': len([s for s in scores if s >= 0.05]),
            'negative_posts': len([s for s in scores if s <= -0.05]),
            'neutral_posts': len([s for s in scores if -0.05 < s < 0.05])
        }
        
        return jsonify({
            'results': results,
            'summary': summary
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Get port from environment variable (for deployment) or use 5000 (for local)
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)