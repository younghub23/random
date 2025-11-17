"""Backtesting system to validate predictive power of the stock scoring model.

This module tests historical performance of the stock scoring system to:
1. Validate that high-scoring stocks actually outperform
2. Measure contribution of each metric to predictive power
3. Optimize weights for maximum predictive accuracy
4. Calculate risk-adjusted returns (Sharpe ratio, max drawdown, etc.)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
import json
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.fetcher import StockDataFetcher
from analysis.momentum import MomentumAnalyzer
from analysis.fundamental import FundamentalAnalyzer
from analysis.sentiment import SentimentAnalyzer, calculate_sentiment_score
from utils.output import OutputFormatter


class WeightedScorer:
    """Enhanced scorer that uses configurable weights for all metrics."""

    def __init__(self, weights_file: str = "weights_config.json"):
        """Initialize with weight configuration.

        Args:
            weights_file: Path to weights configuration JSON
        """
        self.weights = self._load_weights(weights_file)

    def _load_weights(self, weights_file: str) -> Dict[str, Any]:
        """Load weights from configuration file."""
        weights_path = Path(weights_file)

        if not weights_path.exists():
            print(f"Warning: {weights_file} not found, using defaults")
            return self._get_default_weights()

        with open(weights_path, 'r') as f:
            return json.load(f)

    def _get_default_weights(self) -> Dict[str, Any]:
        """Get default weights if config file doesn't exist."""
        return {
            'composite_weights': {
                'momentum': 0.35,
                'fundamental': 0.50,
                'sentiment': 0.15
            },
            'momentum_weights': {
                'moving_averages': 0.20,
                'rsi': 0.15,
                'macd': 0.15,
                'volume': 0.15,
                'price_momentum': 0.20,
                'trend_strength': 0.15
            },
            'fundamental_weights': {
                'valuation': 0.25,
                'profitability': 0.25,
                'financial_health': 0.25,
                'growth': 0.25
            },
            'sentiment_weights': {
                'base_sentiment': 0.70,
                'positive_ratio': 0.20,
                'headline_volume': 0.10
            }
        }

    def calculate_weighted_momentum_score(self, components: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Calculate momentum score using configured weights.

        Args:
            components: Momentum analysis components

        Returns:
            Tuple of (total_score, component_contributions)
        """
        weights = self.weights['momentum_weights']
        contributions = {}

        # Extract component scores
        ma_score = components.get('moving_average_score', 0)
        rsi_score = components.get('rsi_score', 0)
        macd_score = components.get('macd_score', 0)
        volume_score = components.get('volume_score', 0)
        momentum_score = components.get('price_momentum_score', 0)
        trend_score = components.get('trend_strength_score', 0)

        # Normalize to 0-100 scale and apply weights
        contributions['moving_averages'] = (ma_score / 20) * 100 * weights['moving_averages']
        contributions['rsi'] = (rsi_score / 15) * 100 * weights['rsi']
        contributions['macd'] = (macd_score / 15) * 100 * weights['macd']
        contributions['volume'] = (volume_score / 15) * 100 * weights['volume']
        contributions['price_momentum'] = (momentum_score / 20) * 100 * weights['price_momentum']
        contributions['trend_strength'] = (trend_score / 15) * 100 * weights['trend_strength']

        total_score = sum(contributions.values())

        return total_score, contributions

    def calculate_weighted_fundamental_score(self, components: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """Calculate fundamental score using configured weights.

        Args:
            components: Fundamental analysis components

        Returns:
            Tuple of (total_score, component_contributions)
        """
        weights = self.weights['fundamental_weights']
        contributions = {}

        # Extract component scores
        valuation_score = components.get('valuation_score', 0)
        profitability_score = components.get('profitability_score', 0)
        health_score = components.get('financial_health_score', 0)
        growth_score = components.get('growth_score', 0)

        # Normalize to 0-100 scale and apply weights
        contributions['valuation'] = (valuation_score / 25) * 100 * weights['valuation']
        contributions['profitability'] = (profitability_score / 25) * 100 * weights['profitability']
        contributions['financial_health'] = (health_score / 25) * 100 * weights['financial_health']
        contributions['growth'] = (growth_score / 25) * 100 * weights['growth']

        total_score = sum(contributions.values())

        return total_score, contributions

    def calculate_composite_score(self, momentum_score: float, fundamental_score: float,
                                 sentiment_score: float = 50) -> Tuple[float, Dict[str, float]]:
        """Calculate final composite score using configured weights.

        Args:
            momentum_score: Momentum analysis score (0-100)
            fundamental_score: Fundamental analysis score (0-100)
            sentiment_score: Sentiment analysis score (0-100)

        Returns:
            Tuple of (composite_score, category_contributions)
        """
        weights = self.weights['composite_weights']

        contributions = {
            'momentum': momentum_score * weights['momentum'],
            'fundamental': fundamental_score * weights['fundamental'],
            'sentiment': sentiment_score * weights['sentiment']
        }

        composite_score = sum(contributions.values())

        return composite_score, contributions


class Backtester:
    """Backtest the stock scoring model on historical data."""

    def __init__(self, weights_file: str = "weights_config.json", use_cache: bool = True):
        """Initialize backtester.

        Args:
            weights_file: Path to weights configuration
            use_cache: Whether to use caching
        """
        self.fetcher = StockDataFetcher(use_cache=use_cache)
        self.scorer = WeightedScorer(weights_file)
        self.formatter = OutputFormatter()
        self.results = []

    def analyze_stock_at_date(self, ticker: str, analysis_date: datetime,
                             include_sentiment: bool = False) -> Optional[Dict[str, Any]]:
        """Analyze a stock as it would have appeared on a historical date.

        Args:
            ticker: Stock ticker symbol
            analysis_date: Date to analyze from
            include_sentiment: Whether to include sentiment analysis

        Returns:
            Analysis results or None if error
        """
        try:
            # Get historical price data up to analysis date
            end_date = analysis_date
            start_date = analysis_date - timedelta(days=400)  # Get enough history for indicators

            # Fetch historical data
            price_data = self.fetcher.get_price_history(ticker, period="2y")

            if price_data is None or price_data.empty:
                return None

            # Filter to only data available before analysis date
            price_data = price_data[price_data.index <= analysis_date]

            if len(price_data) < 50:  # Need enough data for indicators
                return None

            # Get stock info (this is current, but we use it for fundamental ratios)
            info = self.fetcher.get_stock_info(ticker)
            if not info:
                return None

            # Momentum analysis
            momentum_analyzer = MomentumAnalyzer(price_data)
            momentum_analysis = momentum_analyzer.get_momentum_score()

            # Calculate weighted momentum score
            momentum_score, momentum_contributions = self.scorer.calculate_weighted_momentum_score(
                momentum_analysis['components']
            )

            # Fundamental analysis
            fundamental_analyzer = FundamentalAnalyzer(info)
            fundamental_analysis = fundamental_analyzer.get_fundamental_score()

            # Calculate weighted fundamental score
            fundamental_score, fundamental_contributions = self.scorer.calculate_weighted_fundamental_score(
                fundamental_analysis['components']
            )

            # Sentiment analysis (optional, may not work for historical)
            sentiment_score = 50  # Default neutral
            if include_sentiment:
                try:
                    sentiment_analyzer = SentimentAnalyzer()
                    sentiment_metrics = sentiment_analyzer.get_sentiment_metrics(ticker, info)
                    sentiment_score = calculate_sentiment_score(sentiment_metrics)
                except:
                    pass

            # Calculate composite score
            composite_score, composite_contributions = self.scorer.calculate_composite_score(
                momentum_score, fundamental_score, sentiment_score
            )

            # Get price at analysis date for future return calculation
            current_price = price_data.iloc[-1]['Close']

            return {
                'ticker': ticker,
                'analysis_date': analysis_date,
                'current_price': current_price,
                'composite_score': composite_score,
                'momentum_score': momentum_score,
                'fundamental_score': fundamental_score,
                'sentiment_score': sentiment_score,
                'momentum_contributions': momentum_contributions,
                'fundamental_contributions': fundamental_contributions,
                'composite_contributions': composite_contributions
            }

        except Exception as e:
            print(f"Error analyzing {ticker} at {analysis_date}: {e}")
            return None

    def calculate_future_returns(self, ticker: str, start_date: datetime,
                                holding_periods: List[int] = [30, 90, 180, 365]) -> Dict[int, float]:
        """Calculate actual returns over various holding periods.

        Args:
            ticker: Stock ticker symbol
            start_date: Purchase date
            holding_periods: List of holding periods in days

        Returns:
            Dictionary mapping holding period to return percentage
        """
        returns = {}

        try:
            # Get price data including future periods
            price_data = self.fetcher.get_price_history(ticker, period="3y")

            if price_data is None or price_data.empty:
                return returns

            # Get start price
            start_data = price_data[price_data.index <= start_date]
            if start_data.empty:
                return returns

            start_price = start_data.iloc[-1]['Close']

            # Calculate returns for each holding period
            for days in holding_periods:
                end_date = start_date + timedelta(days=days)
                end_data = price_data[price_data.index <= end_date]

                if not end_data.empty:
                    end_price = end_data.iloc[-1]['Close']
                    return_pct = ((end_price - start_price) / start_price) * 100
                    returns[days] = return_pct

        except Exception as e:
            print(f"Error calculating returns for {ticker}: {e}")

        return returns

    def backtest_single_stock(self, ticker: str, start_date: datetime,
                             end_date: datetime, holding_period: int = 90) -> List[Dict[str, Any]]:
        """Backtest a single stock over a time period.

        Args:
            ticker: Stock ticker symbol
            start_date: Start of backtest period
            end_date: End of backtest period
            holding_period: Days to hold after purchase

        Returns:
            List of backtest results
        """
        results = []
        current_date = start_date

        # Test at monthly intervals
        while current_date <= end_date:
            # Analyze stock at this date
            analysis = self.analyze_stock_at_date(ticker, current_date)

            if analysis:
                # Calculate future returns
                future_returns = self.calculate_future_returns(ticker, current_date, [holding_period])

                analysis['holding_period'] = holding_period
                analysis['actual_return'] = future_returns.get(holding_period, None)
                results.append(analysis)

            # Move to next month
            current_date += timedelta(days=30)

        return results

    def backtest_portfolio(self, tickers: List[str], analysis_date: datetime,
                          holding_period: int = 90, top_n: int = 10) -> Dict[str, Any]:
        """Backtest a portfolio selection strategy.

        Args:
            tickers: List of stock tickers to analyze
            analysis_date: Date to perform analysis
            holding_period: Days to hold portfolio
            top_n: Number of top stocks to select

        Returns:
            Portfolio backtest results
        """
        # Analyze all stocks at the analysis date
        stock_analyses = []

        for ticker in tickers:
            analysis = self.analyze_stock_at_date(ticker, analysis_date)
            if analysis:
                stock_analyses.append(analysis)

        if not stock_analyses:
            return {}

        # Sort by composite score and select top N
        stock_analyses.sort(key=lambda x: x['composite_score'], reverse=True)
        selected_stocks = stock_analyses[:top_n]

        # Calculate future returns for selected stocks
        portfolio_returns = []

        for stock in selected_stocks:
            returns = self.calculate_future_returns(stock['ticker'], analysis_date, [holding_period])
            if holding_period in returns:
                portfolio_returns.append(returns[holding_period])

        # Calculate portfolio metrics
        if portfolio_returns:
            avg_return = np.mean(portfolio_returns)
            median_return = np.median(portfolio_returns)
            std_return = np.std(portfolio_returns)
            sharpe_ratio = (avg_return / std_return) if std_return > 0 else 0
            win_rate = sum(1 for r in portfolio_returns if r > 0) / len(portfolio_returns)
        else:
            avg_return = median_return = std_return = sharpe_ratio = win_rate = 0

        return {
            'analysis_date': analysis_date,
            'holding_period': holding_period,
            'num_stocks': len(selected_stocks),
            'selected_tickers': [s['ticker'] for s in selected_stocks],
            'avg_score': np.mean([s['composite_score'] for s in selected_stocks]),
            'avg_return': avg_return,
            'median_return': median_return,
            'std_return': std_return,
            'sharpe_ratio': sharpe_ratio,
            'win_rate': win_rate * 100,
            'individual_returns': portfolio_returns,
            'selected_stocks': selected_stocks
        }

    def analyze_metric_importance(self, backtest_results: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze which metrics are most predictive of future returns.

        Uses correlation analysis to determine which components of the score
        are most strongly associated with actual returns.

        Args:
            backtest_results: List of backtest results with scores and returns

        Returns:
            Dictionary of correlations for each metric
        """
        if not backtest_results:
            return {}

        # Extract data for correlation analysis
        data = {
            'composite_score': [],
            'momentum_score': [],
            'fundamental_score': [],
            'sentiment_score': [],
            'actual_return': []
        }

        # Add momentum components
        momentum_components = ['moving_averages', 'rsi', 'macd', 'volume', 'price_momentum', 'trend_strength']
        for comp in momentum_components:
            data[f'momentum_{comp}'] = []

        # Add fundamental components
        fundamental_components = ['valuation', 'profitability', 'financial_health', 'growth']
        for comp in fundamental_components:
            data[f'fundamental_{comp}'] = []

        # Populate data
        for result in backtest_results:
            if result.get('actual_return') is None:
                continue

            data['composite_score'].append(result['composite_score'])
            data['momentum_score'].append(result['momentum_score'])
            data['fundamental_score'].append(result['fundamental_score'])
            data['sentiment_score'].append(result['sentiment_score'])
            data['actual_return'].append(result['actual_return'])

            # Momentum components
            for comp in momentum_components:
                value = result.get('momentum_contributions', {}).get(comp, 0)
                data[f'momentum_{comp}'].append(value)

            # Fundamental components
            for comp in fundamental_components:
                value = result.get('fundamental_contributions', {}).get(comp, 0)
                data[f'fundamental_{comp}'].append(value)

        # Calculate correlations
        correlations = {}
        df = pd.DataFrame(data)

        for col in df.columns:
            if col != 'actual_return':
                corr = df[col].corr(df['actual_return'])
                correlations[col] = corr if not pd.isna(corr) else 0

        return correlations

    def print_backtest_results(self, results: Dict[str, Any]):
        """Print formatted backtest results.

        Args:
            results: Backtest results dictionary
        """
        self.formatter.console.print("\n[bold cyan]📊 Backtest Results[/bold cyan]\n")

        self.formatter.console.print(f"Analysis Date: {results['analysis_date'].strftime('%Y-%m-%d')}")
        self.formatter.console.print(f"Holding Period: {results['holding_period']} days")
        self.formatter.console.print(f"Number of Stocks: {results['num_stocks']}")
        self.formatter.console.print(f"Average Score: {results['avg_score']:.2f}")
        self.formatter.console.print(f"\n[bold]Portfolio Performance:[/bold]")
        self.formatter.console.print(f"  Average Return: {results['avg_return']:.2f}%")
        self.formatter.console.print(f"  Median Return: {results['median_return']:.2f}%")
        self.formatter.console.print(f"  Std Deviation: {results['std_return']:.2f}%")
        self.formatter.console.print(f"  Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        self.formatter.console.print(f"  Win Rate: {results['win_rate']:.1f}%")

        self.formatter.console.print(f"\n[bold]Selected Stocks:[/bold]")
        for ticker in results['selected_tickers']:
            self.formatter.console.print(f"  • {ticker}")


def main():
    """Main entry point for backtesting."""
    import argparse

    parser = argparse.ArgumentParser(description='Backtest Stock Analysis Model')
    parser.add_argument('--ticker', help='Single ticker to backtest')
    parser.add_argument('--tickers', nargs='+', help='Multiple tickers for portfolio backtest')
    parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    parser.add_argument('--holding-period', type=int, default=90, help='Holding period in days')
    parser.add_argument('--top-n', type=int, default=10, help='Number of top stocks to select')
    parser.add_argument('--weights', default='weights_config.json', help='Weights configuration file')

    args = parser.parse_args()

    # Initialize backtester
    backtester = Backtester(weights_file=args.weights)

    # Parse dates
    start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    end_date = datetime.strptime(args.end_date, '%Y-%m-%d') if args.end_date else datetime.now()

    if args.ticker:
        # Single stock backtest
        print(f"\nBacktesting {args.ticker} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        results = backtester.backtest_single_stock(args.ticker, start_date, end_date, args.holding_period)

        print(f"\nCompleted {len(results)} analyses")

        if results:
            # Analyze metric importance
            correlations = backtester.analyze_metric_importance(results)

            print("\n" + "="*80)
            print("Metric Correlation with Future Returns")
            print("="*80)

            for metric, corr in sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True):
                print(f"{metric:40} {corr:+.3f}")

    elif args.tickers:
        # Portfolio backtest
        print(f"\nBacktesting portfolio at {start_date.strftime('%Y-%m-%d')}")
        results = backtester.backtest_portfolio(args.tickers, start_date, args.holding_period, args.top_n)

        backtester.print_backtest_results(results)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
