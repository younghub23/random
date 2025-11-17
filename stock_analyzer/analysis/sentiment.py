"""Sentiment analysis module for stock analysis."""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time
import re


class SentimentAnalyzer:
    """Analyzes sentiment from news articles and social media."""

    def __init__(self, use_cache: bool = True):
        """Initialize sentiment analyzer.

        Args:
            use_cache: Whether to use caching
        """
        self.use_cache = use_cache
        # Simple sentiment word lists for basic analysis
        self.positive_words = set([
            'gain', 'gains', 'profit', 'profitable', 'growth', 'growing', 'increase', 'increased',
            'surge', 'surged', 'rally', 'rallied', 'beat', 'beats', 'outperform', 'strong',
            'upgrade', 'upgraded', 'bullish', 'positive', 'excellent', 'success', 'successful',
            'innovation', 'innovative', 'breakthrough', 'record', 'high', 'higher', 'up',
            'confidence', 'optimistic', 'boom', 'expand', 'expansion', 'momentum', 'winner'
        ])

        self.negative_words = set([
            'loss', 'losses', 'decline', 'declining', 'decrease', 'decreased', 'fall', 'fell',
            'drop', 'dropped', 'plunge', 'plunged', 'crash', 'crashed', 'miss', 'missed',
            'underperform', 'weak', 'downgrade', 'downgraded', 'bearish', 'negative', 'poor',
            'failure', 'failed', 'concern', 'concerns', 'risk', 'risks', 'uncertainty',
            'worry', 'worries', 'pessimistic', 'low', 'lower', 'down', 'warning', 'warned'
        ])

    def get_news_headlines(self, ticker: str, company_name: str = None, max_results: int = 10) -> List[Dict[str, str]]:
        """Fetch recent news headlines for a stock.

        Args:
            ticker: Stock ticker symbol
            company_name: Company name (if available)
            max_results: Maximum number of headlines to fetch

        Returns:
            List of news items with title, source, and date
        """
        headlines = []

        try:
            # Try Google News search
            search_query = f"{ticker} stock {company_name if company_name else ''}"
            search_url = f"https://www.google.com/search?q={search_query}&tbm=nws"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(search_url, headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Parse news items
                for item in soup.find_all('div', class_='SoaBEf')[:max_results]:
                    try:
                        title_elem = item.find('div', class_='MBeuO')
                        source_elem = item.find('div', class_='NUnG9d')

                        if title_elem:
                            headlines.append({
                                'title': title_elem.get_text(),
                                'source': source_elem.get_text() if source_elem else 'Unknown',
                                'date': 'Recent'
                            })
                    except Exception:
                        continue

            # If Google News didn't work, try a simpler approach with Yahoo Finance
            if not headlines:
                headlines = self._get_yahoo_headlines(ticker)

        except Exception as e:
            print(f"Warning: Could not fetch news for {ticker}: {e}")

        return headlines[:max_results]

    def _get_yahoo_headlines(self, ticker: str) -> List[Dict[str, str]]:
        """Fallback method to get headlines from Yahoo Finance.

        Args:
            ticker: Stock ticker symbol

        Returns:
            List of news items
        """
        headlines = []

        try:
            import yfinance as yf
            stock = yf.Ticker(ticker)
            news = stock.news

            if news:
                for item in news[:10]:
                    headlines.append({
                        'title': item.get('title', ''),
                        'source': item.get('publisher', 'Yahoo Finance'),
                        'date': datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%Y-%m-%d')
                    })
        except Exception as e:
            print(f"Warning: Yahoo Finance news fetch failed for {ticker}: {e}")

        return headlines

    def analyze_text_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of a text using simple word matching.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with sentiment metrics
        """
        if not text:
            return {'score': 50, 'positive_count': 0, 'negative_count': 0, 'neutral': True}

        # Convert to lowercase and split into words
        words = re.findall(r'\b\w+\b', text.lower())

        # Count positive and negative words
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)

        # Calculate sentiment score (0-100)
        total_sentiment_words = positive_count + negative_count

        if total_sentiment_words == 0:
            sentiment_score = 50  # Neutral
        else:
            # Score: 0 = very negative, 50 = neutral, 100 = very positive
            sentiment_ratio = positive_count / total_sentiment_words
            sentiment_score = sentiment_ratio * 100

        return {
            'score': sentiment_score,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral': total_sentiment_words == 0,
            'bullish': sentiment_score > 60,
            'bearish': sentiment_score < 40
        }

    def get_stock_sentiment(self, ticker: str, company_name: str = None) -> Dict[str, Any]:
        """Get overall sentiment score for a stock based on recent news.

        Args:
            ticker: Stock ticker symbol
            company_name: Company name (optional)

        Returns:
            Dictionary with sentiment analysis results
        """
        # Fetch news headlines
        headlines = self.get_news_headlines(ticker, company_name, max_results=20)

        if not headlines:
            return {
                'sentiment_score': 50,  # Neutral default
                'headline_count': 0,
                'positive_headlines': 0,
                'negative_headlines': 0,
                'neutral_headlines': 0,
                'avg_sentiment': 50,
                'sentiment_strength': 'Neutral',
                'recent_headlines': []
            }

        # Analyze each headline
        sentiment_scores = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0

        analyzed_headlines = []

        for headline in headlines:
            sentiment = self.analyze_text_sentiment(headline['title'])
            sentiment_scores.append(sentiment['score'])

            if sentiment['bullish']:
                positive_count += 1
                headline['sentiment'] = 'Positive'
            elif sentiment['bearish']:
                negative_count += 1
                headline['sentiment'] = 'Negative'
            else:
                neutral_count += 1
                headline['sentiment'] = 'Neutral'

            headline['sentiment_score'] = sentiment['score']
            analyzed_headlines.append(headline)

        # Calculate average sentiment
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 50

        # Determine sentiment strength
        if avg_sentiment >= 70:
            strength = 'Very Positive'
        elif avg_sentiment >= 60:
            strength = 'Positive'
        elif avg_sentiment >= 40:
            strength = 'Neutral'
        elif avg_sentiment >= 30:
            strength = 'Negative'
        else:
            strength = 'Very Negative'

        return {
            'sentiment_score': avg_sentiment,
            'headline_count': len(headlines),
            'positive_headlines': positive_count,
            'negative_headlines': negative_count,
            'neutral_headlines': neutral_count,
            'avg_sentiment': avg_sentiment,
            'sentiment_strength': strength,
            'recent_headlines': analyzed_headlines[:5]  # Top 5 for display
        }

    def get_sentiment_metrics(self, ticker: str, info: Dict[str, Any]) -> Dict[str, Any]:
        """Get sentiment metrics for scoring.

        Args:
            ticker: Stock ticker symbol
            info: Stock info dictionary

        Returns:
            Dictionary with sentiment metrics for scoring
        """
        company_name = info.get('longName', ticker)
        sentiment = self.get_stock_sentiment(ticker, company_name)

        return {
            'sentiment_score': sentiment['sentiment_score'],
            'sentiment_strength': sentiment['sentiment_strength'],
            'headline_count': sentiment['headline_count'],
            'positive_ratio': sentiment['positive_headlines'] / max(sentiment['headline_count'], 1),
            'negative_ratio': sentiment['negative_headlines'] / max(sentiment['headline_count'], 1),
            'recent_headlines': sentiment['recent_headlines']
        }


# Weight-based sentiment scoring for integration
def calculate_sentiment_score(sentiment_metrics: Dict[str, Any]) -> float:
    """Calculate 0-100 sentiment score based on metrics.

    Weight breakdown:
    - Sentiment Score (0-100): 70% weight - Direct sentiment from headlines
    - Positive Ratio: 20% weight - Proportion of positive headlines
    - Headline Volume: 10% weight - More headlines = more market attention

    Args:
        sentiment_metrics: Dictionary with sentiment metrics

    Returns:
        Weighted sentiment score (0-100)
    """
    # Base sentiment score (0-100)
    base_score = sentiment_metrics.get('sentiment_score', 50)

    # Positive ratio bonus (0-20 points)
    positive_ratio = sentiment_metrics.get('positive_ratio', 0)
    positive_bonus = positive_ratio * 20

    # Headline volume factor (0-10 points)
    headline_count = sentiment_metrics.get('headline_count', 0)
    if headline_count >= 20:
        volume_bonus = 10
    elif headline_count >= 10:
        volume_bonus = 7
    elif headline_count >= 5:
        volume_bonus = 4
    else:
        volume_bonus = headline_count * 0.8

    # Calculate weighted score
    # Base score: 70%, Positive bonus: 20%, Volume bonus: 10%
    weighted_score = (base_score * 0.7) + positive_bonus + volume_bonus

    # Ensure score is within 0-100
    return max(0, min(100, weighted_score))
