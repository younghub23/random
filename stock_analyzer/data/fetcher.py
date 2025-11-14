"""Data fetching module using yfinance API."""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from data.cache import DataCache
from utils.config import Config


class StockDataFetcher:
    """Fetches stock data from yfinance with caching support."""

    def __init__(self, use_cache: bool = True):
        """Initialize the data fetcher.

        Args:
            use_cache: Whether to use caching
        """
        self.use_cache = use_cache and Config.CACHE_ENABLED
        self.cache = DataCache(Config.CACHE_DIRECTORY, Config.CACHE_EXPIRY_HOURS) if self.use_cache else None

    def get_stock_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get basic stock information.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with stock information or None if error
        """
        cache_key = f"{ticker}_info"

        # Try cache first
        if self.use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Validate that we got actual data
            if not info or 'symbol' not in info:
                print(f"Error: Unable to fetch data for {ticker}. Invalid ticker symbol.")
                return None

            # Cache the result
            if self.use_cache:
                self.cache.set(cache_key, info)

            return info

        except Exception as e:
            print(f"Error fetching info for {ticker}: {e}")
            return None

    def get_price_history(self, ticker: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """Get historical price data.

        Args:
            ticker: Stock ticker symbol
            period: Time period (e.g., '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')

        Returns:
            DataFrame with price history or None if error
        """
        cache_key = f"{ticker}_price_{period}"

        # Try cache first
        if self.use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)

            if df.empty:
                print(f"Error: No price data available for {ticker}")
                return None

            # Cache the result
            if self.use_cache:
                self.cache.set(cache_key, df)

            return df

        except Exception as e:
            print(f"Error fetching price history for {ticker}: {e}")
            return None

    def get_financial_statements(self, ticker: str) -> Optional[Dict[str, pd.DataFrame]]:
        """Get financial statements (income statement, balance sheet, cash flow).

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with financial statements or None if error
        """
        cache_key = f"{ticker}_financials"

        # Try cache first
        if self.use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        try:
            stock = yf.Ticker(ticker)

            financials = {
                'income_statement': stock.financials,
                'balance_sheet': stock.balance_sheet,
                'cash_flow': stock.cashflow,
                'quarterly_income': stock.quarterly_financials,
                'quarterly_balance': stock.quarterly_balance_sheet,
                'quarterly_cashflow': stock.quarterly_cashflow
            }

            # Cache the result
            if self.use_cache:
                self.cache.set(cache_key, financials)

            return financials

        except Exception as e:
            print(f"Error fetching financials for {ticker}: {e}")
            return None

    def get_recommendations(self, ticker: str) -> Optional[pd.DataFrame]:
        """Get analyst recommendations.

        Args:
            ticker: Stock ticker symbol

        Returns:
            DataFrame with recommendations or None if error
        """
        cache_key = f"{ticker}_recommendations"

        # Try cache first
        if self.use_cache:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        try:
            stock = yf.Ticker(ticker)
            recommendations = stock.recommendations

            if recommendations is None or recommendations.empty:
                return None

            # Cache the result
            if self.use_cache:
                self.cache.set(cache_key, recommendations)

            return recommendations

        except Exception as e:
            print(f"Error fetching recommendations for {ticker}: {e}")
            return None

    def validate_ticker(self, ticker: str) -> bool:
        """Validate if a ticker symbol is valid.

        Args:
            ticker: Stock ticker symbol

        Returns:
            True if valid, False otherwise
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return 'symbol' in info and info.get('regularMarketPrice') is not None
        except:
            return False

    def get_multiple_tickers(self, tickers: list) -> Dict[str, Dict[str, Any]]:
        """Fetch data for multiple tickers.

        Args:
            tickers: List of ticker symbols

        Returns:
            Dictionary mapping ticker to stock info
        """
        results = {}

        for ticker in tickers:
            info = self.get_stock_info(ticker)
            if info:
                results[ticker] = info

        return results

    def clear_cache(self, ticker: Optional[str] = None):
        """Clear cached data.

        Args:
            ticker: Specific ticker to clear, or None to clear all
        """
        if not self.use_cache:
            return

        if ticker:
            # Clear all cache entries for this ticker
            for suffix in ['info', 'price_1y', 'financials', 'recommendations']:
                self.cache.invalidate(f"{ticker}_{suffix}")
        else:
            # Clear all cache
            count = self.cache.clear_all()
            print(f"Cleared {count} cache files")
