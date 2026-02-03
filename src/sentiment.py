import yfinance as yf
from textblob import TextBlob
import pandas as pd

class SentimentAnalyzer:
    def __init__(self):
        pass

    def get_news_sentiment(self, ticker):
        """
        Fetches news from yfinance and calculates average sentiment.
        Returns: (sentiment_score, sentiment_label, news_list)
        """
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            
            if not news:
                return 0, "Neutral", []

            total_polarity = 0
            count = 0
            analyzed_news = []

            for item in news:
                title = item.get('title', '')
                if not title:
                    continue
                    
                analysis = TextBlob(title)
                polarity = analysis.sentiment.polarity
                total_polarity += polarity
                count += 1
                
                analyzed_news.append({
                    'title': title,
                    'link': item.get('link', '#'),
                    'publisher': item.get('publisher', 'Unknown'),
                    'polarity': polarity
                })

            if count == 0:
                return 0, "Neutral", []

            avg_polarity = total_polarity / count
            
            # Classify
            if avg_polarity > 0.1:
                label = "Positive"
            elif avg_polarity < -0.1:
                label = "Negative"
            else:
                label = "Neutral"
                
            return avg_polarity, label, analyzed_news[:5] # Return top 5 recent news

        except Exception as e:
            print(f"Sentiment Error: {e}")
            return 0, "Error", []
