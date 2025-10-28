# VADER Sentiment Analyzer 📈

A web application that analyzes Reddit sentiment for stocks using VADER sentiment analysis.

## Features

- 🎯 Real-time sentiment analysis of Reddit posts
- 📊 Visual sentiment dashboard with statistics
- 🔍 Searches both stock tickers and company names
- 🧹 Advanced text preprocessing (removes emojis, URLs, etc.)
- 📱 Responsive design

## Tech Stack

- **Backend**: Flask, PRAW (Reddit API), VADER Sentiment
- **Frontend**: HTML, CSS, JavaScript
- **Data Processing**: Pandas, Regex

## Installation

1. Clone the repository:
```bash
git clone https://github.com/shubhamprabhukhanolkar/vader-sentiment-analyzer.git
cd vader-sentiment-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `secrets.ini` with your Reddit API credentials:
```ini
[REDDIT]
CLIENT_ID = your_client_id
CLIENT_SECRET = your_client_secret
USER_AGENT = your_user_agent
```

4. Run the application:
```bash
python app.py
```

5. Open browser and go to `http://localhost:5000`

## Getting Reddit API Credentials

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Select "script" type
4. Copy your `client_id` and `client_secret`

## Usage

1. Select a stock from the dropdown (e.g., TSLA, AAPL, GME)
2. Select a subreddit (e.g., wallstreetbets, stocks)
3. Click "Analyze Sentiment"
4. View results with sentiment scores and statistics

## Supported Stocks

TSLA, AAPL, GME, AMC, NVDA, MSFT, GOOGL, AMZN, META, NFLX, AMD, PLTR, BB, NOK, NIO, COIN

## Supported Subreddits

wallstreetbets, stocks, investing, StockMarket, options, pennystocks, Daytrading, SecurityAnalysis

## License

MIT

## Author

Shubham PrabhuKhanolkar
