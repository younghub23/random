"""Sector-specific backtesting and weight optimization.

This module enables backtesting and weight optimization on a sector-by-sector basis,
allowing you to find optimal weights for different types of stocks.

Example: Tech stocks may favor momentum, while utilities may favor fundamentals.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
import json
from pathlib import Path
import sys
import os
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.fetcher import StockDataFetcher
from analysis.momentum import MomentumAnalyzer
from analysis.fundamental import FundamentalAnalyzer
from analysis.sentiment import SentimentAnalyzer, calculate_sentiment_score
from backtest import WeightedScorer
from utils.output import OutputFormatter


class SectorBacktester:
    """Backtest and optimize weights on a sector-by-sector basis."""

    def __init__(self, use_cache: bool = True):
        """Initialize sector backtester.

        Args:
            use_cache: Whether to use caching
        """
        self.fetcher = StockDataFetcher(use_cache=use_cache)
        self.formatter = OutputFormatter()

        # Predefined sector universes
        self.sector_universes = self._get_sector_universes()

    def _get_sector_universes(self) -> Dict[str, List[str]]:
        """Get predefined stock universes by sector.

        Returns:
            Dictionary mapping sector names to lists of tickers
        """
        return {
            'Technology': [
                'AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'AVGO', 'ORCL', 'ADBE',
                'CRM', 'CSCO', 'ACN', 'AMD', 'INTC', 'TXN', 'QCOM', 'INTU',
                'AMAT', 'MU', 'LRCX', 'KLAC', 'SNPS', 'CDNS', 'ASML', 'NOW'
            ],
            'Healthcare': [
                'UNH', 'JNJ', 'LLY', 'ABBV', 'MRK', 'TMO', 'ABT', 'PFE',
                'DHR', 'BMY', 'AMGN', 'GILD', 'CVS', 'CI', 'MDT', 'ISRG',
                'VRTX', 'REGN', 'HUM', 'SYK', 'BSX', 'ELV', 'ZTS', 'IDXX'
            ],
            'Financials': [
                'BRK-B', 'JPM', 'V', 'MA', 'BAC', 'WFC', 'MS', 'GS',
                'AXP', 'BLK', 'C', 'SCHW', 'CB', 'MMC', 'PGR', 'AON',
                'ICE', 'USB', 'TFC', 'PNC', 'BK', 'AIG', 'MET', 'PRU'
            ],
            'Consumer_Discretionary': [
                'AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'LOW', 'TJX',
                'BKNG', 'ABNB', 'CMG', 'MAR', 'GM', 'F', 'ORLY', 'AZO',
                'YUM', 'ROST', 'DHI', 'LEN', 'BBY', 'DG', 'DLTR', 'EBAY'
            ],
            'Consumer_Staples': [
                'WMT', 'PG', 'COST', 'KO', 'PEP', 'PM', 'MO', 'MDLZ',
                'CL', 'KMB', 'GIS', 'HSY', 'K', 'CLX', 'SYY', 'TSN',
                'CAG', 'STZ', 'TAP', 'CPB', 'CHD', 'MKC', 'HRL', 'SJM'
            ],
            'Energy': [
                'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO',
                'OXY', 'HES', 'WMB', 'KMI', 'HAL', 'DVN', 'BKR', 'FANG',
                'MRO', 'APA', 'CTRA', 'EQT', 'OKE', 'TRGP', 'LNG', 'PXD'
            ],
            'Industrials': [
                'UPS', 'RTX', 'HON', 'UNP', 'LMT', 'BA', 'CAT', 'GE',
                'MMM', 'DE', 'FDX', 'NSC', 'ETN', 'CSX', 'EMR', 'ITW',
                'WM', 'GD', 'NOC', 'PH', 'CMI', 'RSG', 'CARR', 'PCAR'
            ],
            'Materials': [
                'LIN', 'APD', 'SHW', 'FCX', 'NEM', 'ECL', 'DD', 'NUE',
                'DOW', 'PPG', 'VMC', 'MLM', 'BALL', 'AVY', 'AMCR', 'CF',
                'MOS', 'ALB', 'FMC', 'CE', 'IP', 'PKG', 'IFF', 'EMN'
            ],
            'Real_Estate': [
                'PLD', 'AMT', 'CCI', 'EQIX', 'PSA', 'SPG', 'WELL', 'DLR',
                'O', 'VICI', 'AVB', 'EQR', 'WY', 'INVH', 'MAA', 'ESS',
                'ARE', 'VTR', 'PEAK', 'UDR', 'BXP', 'FRT', 'REG', 'KIM'
            ],
            'Utilities': [
                'NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE', 'XEL',
                'PCG', 'ED', 'WEC', 'PEG', 'ES', 'AWK', 'DTE', 'PPL',
                'FE', 'EIX', 'ETR', 'AEE', 'CMS', 'CNP', 'NI', 'LNT'
            ],
            'Communication_Services': [
                'GOOGL', 'META', 'DIS', 'NFLX', 'CMCSA', 'T', 'VZ', 'TMUS',
                'CHTR', 'EA', 'TTWO', 'ATVI', 'PARA', 'WBD', 'OMC', 'IPG',
                'NWSA', 'FOXA', 'LYV', 'MTCH', 'PINS', 'SNAP', 'ROKU', 'ZM'
            ]
        }

    def analyze_stock_for_sector(self, ticker: str, analysis_date: datetime,
                                 weights_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Analyze a single stock with given weights.

        Args:
            ticker: Stock ticker
            analysis_date: Date to analyze from
            weights_config: Weight configuration to use

        Returns:
            Analysis results with future returns
        """
        try:
            # Get historical data
            price_data = self.fetcher.get_price_history(ticker, period="2y")
            if price_data is None or price_data.empty:
                return None

            # Filter to analysis date
            price_data = price_data[price_data.index <= analysis_date]
            if len(price_data) < 50:
                return None

            # Get stock info
            info = self.fetcher.get_stock_info(ticker)
            if not info:
                return None

            # Momentum analysis
            momentum_analyzer = MomentumAnalyzer(price_data)
            momentum_analysis = momentum_analyzer.get_momentum_score()

            # Fundamental analysis
            fundamental_analyzer = FundamentalAnalyzer(info)
            fundamental_analysis = fundamental_analyzer.get_fundamental_score()

            # Calculate scores with given weights
            scorer = WeightedScorer()
            scorer.weights = weights_config

            momentum_score, _ = scorer.calculate_weighted_momentum_score(
                momentum_analysis['components']
            )
            fundamental_score, _ = scorer.calculate_weighted_fundamental_score(
                fundamental_analysis['components']
            )

            composite_score, _ = scorer.calculate_composite_score(
                momentum_score, fundamental_score, 50
            )

            # Calculate future returns
            future_returns = self._calculate_future_returns(ticker, analysis_date)

            return {
                'ticker': ticker,
                'analysis_date': analysis_date,
                'composite_score': composite_score,
                'momentum_score': momentum_score,
                'fundamental_score': fundamental_score,
                'returns_30d': future_returns.get(30),
                'returns_90d': future_returns.get(90),
                'returns_180d': future_returns.get(180),
                'returns_365d': future_returns.get(365)
            }

        except Exception as e:
            print(f"Error analyzing {ticker}: {e}")
            return None

    def _calculate_future_returns(self, ticker: str, start_date: datetime) -> Dict[int, float]:
        """Calculate future returns for various periods."""
        returns = {}
        try:
            price_data = self.fetcher.get_price_history(ticker, period="3y")
            if price_data is None or price_data.empty:
                return returns

            start_data = price_data[price_data.index <= start_date]
            if start_data.empty:
                return returns

            start_price = start_data.iloc[-1]['Close']

            for days in [30, 90, 180, 365]:
                end_date = start_date + timedelta(days=days)
                end_data = price_data[price_data.index <= end_date]
                if not end_data.empty:
                    end_price = end_data.iloc[-1]['Close']
                    returns[days] = ((end_price - start_price) / start_price) * 100

        except Exception as e:
            print(f"Error calculating returns for {ticker}: {e}")

        return returns

    def backtest_sector(self, sector: str, analysis_date: datetime,
                       weights_config: Dict[str, Any], holding_period: int = 90) -> Dict[str, Any]:
        """Backtest a sector with given weights.

        Args:
            sector: Sector name
            analysis_date: Date to analyze
            weights_config: Weight configuration
            holding_period: Holding period in days

        Returns:
            Sector backtest results
        """
        print(f"\n{'='*80}")
        print(f"Backtesting {sector} Sector")
        print(f"Date: {analysis_date.strftime('%Y-%m-%d')}, Holding Period: {holding_period} days")
        print(f"{'='*80}\n")

        tickers = self.sector_universes.get(sector, [])
        if not tickers:
            print(f"Unknown sector: {sector}")
            return {}

        results = []
        print(f"Analyzing {len(tickers)} stocks in {sector}...")

        for i, ticker in enumerate(tickers, 1):
            print(f"[{i}/{len(tickers)}] {ticker}...", end=' ')

            result = self.analyze_stock_for_sector(ticker, analysis_date, weights_config)

            if result:
                results.append(result)
                return_key = f'returns_{holding_period}d'
                ret = result.get(return_key)
                if ret is not None:
                    print(f"✓ Score: {result['composite_score']:.1f}, Return: {ret:+.1f}%")
                else:
                    print(f"✓ Score: {result['composite_score']:.1f}, Return: N/A")
            else:
                print("✗ Failed")

        if not results:
            return {}

        # Calculate metrics
        return_key = f'returns_{holding_period}d'
        returns = [r[return_key] for r in results if r.get(return_key) is not None]
        scores = [r['composite_score'] for r in results]

        if returns:
            avg_return = np.mean(returns)
            median_return = np.median(returns)
            std_return = np.std(returns)
            sharpe = (avg_return / std_return) if std_return > 0 else 0
            win_rate = sum(1 for r in returns if r > 0) / len(returns) * 100

            # Calculate correlation
            score_return_pairs = [(r['composite_score'], r[return_key])
                                 for r in results if r.get(return_key) is not None]
            if len(score_return_pairs) > 1:
                scores_arr = np.array([s for s, _ in score_return_pairs])
                returns_arr = np.array([r for _, r in score_return_pairs])
                correlation = np.corrcoef(scores_arr, returns_arr)[0, 1]
            else:
                correlation = 0
        else:
            avg_return = median_return = std_return = sharpe = win_rate = correlation = 0

        return {
            'sector': sector,
            'analysis_date': analysis_date,
            'holding_period': holding_period,
            'num_stocks_analyzed': len(results),
            'num_stocks_with_returns': len(returns),
            'avg_return': avg_return,
            'median_return': median_return,
            'std_return': std_return,
            'sharpe_ratio': sharpe,
            'win_rate': win_rate,
            'correlation': correlation,
            'avg_score': np.mean(scores),
            'results': results
        }

    def optimize_weights_for_sector(self, sector: str, analysis_date: datetime,
                                    holding_period: int = 90) -> pd.DataFrame:
        """Optimize weights for a specific sector.

        Args:
            sector: Sector name
            analysis_date: Date to analyze
            holding_period: Holding period in days

        Returns:
            DataFrame with optimization results
        """
        print(f"\n{'='*80}")
        print(f"OPTIMIZING WEIGHTS FOR {sector.upper()} SECTOR")
        print(f"{'='*80}\n")

        # Test different weight combinations
        momentum_weights = [0.2, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6]
        fundamental_weights = [0.3, 0.4, 0.5, 0.6, 0.7]

        results = []
        total_combos = len(momentum_weights) * len(fundamental_weights)
        tested = 0

        for momentum_weight in momentum_weights:
            for fundamental_weight in fundamental_weights:
                sentiment_weight = 1.0 - momentum_weight - fundamental_weight

                if sentiment_weight < 0 or sentiment_weight > 0.3:
                    continue

                tested += 1
                print(f"[{tested}/{total_combos}] Testing M:{momentum_weight:.2f} F:{fundamental_weight:.2f} S:{sentiment_weight:.2f}...")

                # Create weight config
                weights_config = {
                    'composite_weights': {
                        'momentum': momentum_weight,
                        'fundamental': fundamental_weight,
                        'sentiment': sentiment_weight
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

                # Backtest this configuration
                backtest_result = self.backtest_sector(
                    sector, analysis_date, weights_config, holding_period
                )

                if backtest_result:
                    results.append({
                        'sector': sector,
                        'momentum_weight': momentum_weight,
                        'fundamental_weight': fundamental_weight,
                        'sentiment_weight': sentiment_weight,
                        'avg_return': backtest_result['avg_return'],
                        'median_return': backtest_result['median_return'],
                        'sharpe_ratio': backtest_result['sharpe_ratio'],
                        'win_rate': backtest_result['win_rate'],
                        'correlation': backtest_result['correlation'],
                        'num_stocks': backtest_result['num_stocks_with_returns']
                    })

        df = pd.DataFrame(results)

        if not df.empty:
            df = df.sort_values('avg_return', ascending=False)

            print("\n" + "="*80)
            print(f"OPTIMIZATION RESULTS FOR {sector.upper()}")
            print("="*80)
            print("\nTop 5 Weight Configurations:")
            print(df.head(5).to_string(index=False))

            # Save results
            output_file = f"sector_optimization_{sector}_{analysis_date.strftime('%Y%m%d')}.csv"
            df.to_csv(output_file, index=False)
            print(f"\n✓ Results saved to {output_file}")

        return df

    def optimize_all_sectors(self, analysis_date: datetime, holding_period: int = 90,
                            sectors: Optional[List[str]] = None) -> Dict[str, pd.DataFrame]:
        """Optimize weights for all sectors.

        Args:
            analysis_date: Date to analyze
            holding_period: Holding period in days
            sectors: List of sectors (None = all)

        Returns:
            Dictionary mapping sector to results DataFrame
        """
        if sectors is None:
            sectors = list(self.sector_universes.keys())

        all_results = {}

        for sector in sectors:
            print(f"\n{'#'*80}")
            print(f"# SECTOR: {sector.upper()}")
            print(f"{'#'*80}")

            results_df = self.optimize_weights_for_sector(sector, analysis_date, holding_period)
            all_results[sector] = results_df

        # Create summary comparison
        self._print_sector_comparison(all_results)

        return all_results

    def _print_sector_comparison(self, sector_results: Dict[str, pd.DataFrame]):
        """Print comparison of optimal weights across sectors.

        Args:
            sector_results: Dictionary of sector results
        """
        print("\n" + "="*80)
        print("SECTOR COMPARISON - OPTIMAL WEIGHTS")
        print("="*80 + "\n")

        comparison = []

        for sector, df in sector_results.items():
            if not df.empty:
                best = df.iloc[0]
                comparison.append({
                    'Sector': sector,
                    'Momentum': f"{best['momentum_weight']:.2f}",
                    'Fundamental': f"{best['fundamental_weight']:.2f}",
                    'Sentiment': f"{best['sentiment_weight']:.2f}",
                    'Avg_Return': f"{best['avg_return']:.2f}%",
                    'Sharpe': f"{best['sharpe_ratio']:.2f}",
                    'Win_Rate': f"{best['win_rate']:.1f}%"
                })

        if comparison:
            comparison_df = pd.DataFrame(comparison)
            print(comparison_df.to_string(index=False))

            # Save summary
            output_file = f"sector_comparison_{datetime.now().strftime('%Y%m%d')}.csv"
            comparison_df.to_csv(output_file, index=False)
            print(f"\n✓ Comparison saved to {output_file}")


def main():
    """Main entry point for sector backtesting."""
    import argparse

    parser = argparse.ArgumentParser(description='Sector-Specific Backtesting and Optimization')

    parser.add_argument('--sector', help='Specific sector to analyze')
    parser.add_argument('--all-sectors', action='store_true', help='Analyze all sectors')
    parser.add_argument('--date', required=True, help='Analysis date (YYYY-MM-DD)')
    parser.add_argument('--holding-period', type=int, default=90, help='Holding period in days')
    parser.add_argument('--list-sectors', action='store_true', help='List available sectors')
    parser.add_argument('--no-cache', action='store_true', help='Disable caching')

    args = parser.parse_args()

    backtester = SectorBacktester(use_cache=not args.no_cache)

    # List sectors
    if args.list_sectors:
        print("\nAvailable Sectors:")
        for sector, tickers in backtester.sector_universes.items():
            print(f"  {sector:30} ({len(tickers)} stocks)")
        return

    # Parse date
    analysis_date = datetime.strptime(args.date, '%Y-%m-%d')

    # Run analysis
    if args.all_sectors:
        backtester.optimize_all_sectors(analysis_date, args.holding_period)

    elif args.sector:
        backtester.optimize_weights_for_sector(args.sector, analysis_date, args.holding_period)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
