"""Batch stock analyzer for analyzing large universes of stocks."""
import pandas as pd
import time
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.fetcher import StockDataFetcher
from analysis.momentum import MomentumAnalyzer
from analysis.fundamental import FundamentalAnalyzer
from analysis.scoring import CompositeScorer
from utils.output import OutputFormatter
from utils.config import Config


class BatchStockAnalyzer:
    """Analyzes a large universe of stocks and finds the best opportunities."""

    def __init__(self, use_cache: bool = True, delay: float = 0.5):
        """Initialize the batch analyzer.

        Args:
            use_cache: Whether to use caching
            delay: Delay in seconds between API calls to avoid rate limits
        """
        self.fetcher = StockDataFetcher(use_cache=use_cache)
        self.formatter = OutputFormatter()
        self.delay = delay
        self.results = []

    def get_stock_universe(self, universe_type: str = "sp500") -> List[str]:
        """Get a list of stock tickers for analysis.

        Args:
            universe_type: Type of universe ('sp500', 'sp1000', 'nasdaq100', 'custom')

        Returns:
            List of ticker symbols
        """
        if universe_type == "sp500":
            return self._get_sp500_tickers()
        elif universe_type == "sp1000":
            return self._get_sp1000_tickers()
        elif universe_type == "nasdaq100":
            return self._get_nasdaq100_tickers()
        else:
            return self._get_custom_universe()

    def _get_sp500_tickers(self) -> List[str]:
        """Fetch S&P 500 tickers from Wikipedia."""
        try:
            import requests
            from bs4 import BeautifulSoup

            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'id': 'constituents'})

            tickers = []
            for row in table.findAll('tr')[1:]:
                ticker = row.findAll('td')[0].text.strip()
                tickers.append(ticker.replace('.', '-'))  # Handle special characters

            return tickers
        except Exception as e:
            print(f"Error fetching S&P 500 tickers: {e}")
            return self._get_fallback_sp500()

    def _get_fallback_sp500(self) -> List[str]:
        """Fallback list of major S&P 500 stocks across sectors."""
        return [
            # Technology
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'ORCL', 'ADBE',
            'CRM', 'CSCO', 'ACN', 'AMD', 'IBM', 'INTC', 'TXN', 'QCOM', 'INTU', 'AMAT',
            # Healthcare
            'UNH', 'JNJ', 'LLY', 'ABBV', 'MRK', 'TMO', 'ABT', 'PFE', 'DHR', 'BMY',
            'AMGN', 'GILD', 'CVS', 'CI', 'MDT', 'ISRG', 'VRTX', 'REGN', 'HUM', 'SYK',
            # Financials
            'BRK-B', 'JPM', 'V', 'MA', 'BAC', 'WFC', 'MS', 'GS', 'AXP', 'BLK',
            'C', 'SCHW', 'CB', 'MMC', 'PGR', 'AON', 'ICE', 'USB', 'TFC', 'PNC',
            # Consumer Discretionary
            'AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'LOW', 'TJX', 'BKNG', 'ABNB',
            'CMG', 'MAR', 'GM', 'F', 'ORLY', 'AZO', 'YUM', 'ROST', 'DHI', 'LEN',
            # Consumer Staples
            'WMT', 'PG', 'COST', 'KO', 'PEP', 'PM', 'MO', 'MDLZ', 'CL', 'KMB',
            'GIS', 'HSY', 'K', 'CLX', 'SYY', 'TSN', 'CAG', 'STZ', 'TAP', 'CPB',
            # Energy
            'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC', 'PSX', 'VLO', 'OXY', 'HES',
            'WMB', 'KMI', 'HAL', 'DVN', 'BKR', 'FANG', 'MRO', 'APA', 'CTRA', 'EQT',
            # Industrials
            'UPS', 'RTX', 'HON', 'UNP', 'LMT', 'BA', 'CAT', 'GE', 'MMM', 'DE',
            'FDX', 'NSC', 'ETN', 'CSX', 'EMR', 'ITW', 'WM', 'GD', 'NOC', 'PH',
            # Materials
            'LIN', 'APD', 'SHW', 'FCX', 'NEM', 'ECL', 'DD', 'NUE', 'DOW', 'PPG',
            'VMC', 'MLM', 'BALL', 'AVY', 'AMCR', 'CF', 'MOS', 'ALB', 'FMC', 'CE',
            # Real Estate
            'PLD', 'AMT', 'CCI', 'EQIX', 'PSA', 'SPG', 'WELL', 'DLR', 'O', 'VICI',
            'AVB', 'EQR', 'WY', 'INVH', 'MAA', 'ESS', 'ARE', 'VTR', 'PEAK', 'UDR',
            # Utilities
            'NEE', 'DUK', 'SO', 'D', 'AEP', 'EXC', 'SRE', 'XEL', 'PCG', 'ED',
            'WEC', 'PEG', 'ES', 'AWK', 'DTE', 'PPL', 'FE', 'EIX', 'ETR', 'AEE',
            # Communication Services
            'GOOGL', 'META', 'DIS', 'NFLX', 'CMCSA', 'T', 'VZ', 'TMUS', 'CHTR', 'EA',
            'TTWO', 'ATVI', 'PARA', 'WBD', 'OMC', 'IPG', 'NWSA', 'FOXA', 'LYV', 'MTCH'
        ]

    def _get_sp1000_tickers(self) -> List[str]:
        """Get Russell 1000 or extended list of tickers."""
        # Start with S&P 500
        tickers = self._get_sp500_tickers()

        # Add mid-cap and additional stocks
        additional_stocks = [
            # Additional Tech
            'PLTR', 'SNOW', 'DDOG', 'NET', 'CRWD', 'ZS', 'OKTA', 'FTNT', 'PANW', 'MDB',
            'TEAM', 'WDAY', 'NOW', 'VEEV', 'DOCU', 'ZM', 'TWLO', 'SPLK', 'RNG', 'BILL',
            # Additional Healthcare
            'MRNA', 'BNTX', 'ILMN', 'ALGN', 'DXCM', 'PODD', 'TDOC', 'EXAS', 'QDEL', 'HOLX',
            # Additional Financials
            'SOFI', 'AFRM', 'UPST', 'SQ', 'PYPL', 'COIN', 'HOOD', 'NU', 'MARA', 'RIOT',
            # Additional Consumer
            'RIVN', 'LCID', 'DASH', 'UBER', 'LYFT', 'ABNB', 'ETSY', 'W', 'CHWY', 'CVNA',
            # Additional Energy
            'FSLR', 'ENPH', 'SEDG', 'RUN', 'NOVA', 'BE', 'PLUG', 'BLNK', 'CHPT', 'QS',
            # REITs
            'IRM', 'CUBE', 'EXR', 'LSI', 'REXR', 'COLD', 'STAG', 'FR', 'KRG', 'BXP',
            # Additional sectors - expand to ~1000
        ]

        return list(set(tickers + additional_stocks))[:1000]

    def _get_nasdaq100_tickers(self) -> List[str]:
        """Get NASDAQ 100 tickers."""
        return [
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'AVGO', 'COST',
            'PEP', 'ADBE', 'CSCO', 'TMUS', 'CMCSA', 'NFLX', 'INTC', 'AMD', 'TXN', 'QCOM',
            'INTU', 'HON', 'AMGN', 'AMAT', 'SBUX', 'ISRG', 'BKNG', 'ADI', 'GILD', 'VRTX',
            'ADP', 'REGN', 'MDLZ', 'LRCX', 'PANW', 'MU', 'PYPL', 'SNPS', 'CDNS', 'ASML',
            'ABNB', 'KLAC', 'MELI', 'MAR', 'CSX', 'CRWD', 'FTNT', 'NXPI', 'ORLY', 'MNST',
            'WDAY', 'ADSK', 'CHTR', 'AEP', 'CTAS', 'PCAR', 'MCHP', 'PAYX', 'KDP', 'DXCM',
            'MRNA', 'CPRT', 'AZN', 'ROST', 'ODFL', 'KHC', 'FAST', 'EXC', 'TEAM', 'CTSH',
            'EA', 'GEHC', 'IDXX', 'BKR', 'VRSK', 'LULU', 'XEL', 'MRVL', 'CSGP', 'CCEP',
            'DDOG', 'ANSS', 'ON', 'ZS', 'BIIB', 'TTWO', 'CDW', 'ILMN', 'GFS', 'WBD',
            'MDB', 'FANG', 'DLTR', 'WBA', 'ZM', 'ALGN', 'EBAY', 'ENPH', 'SIRI', 'JD'
        ]

    def _get_custom_universe(self) -> List[str]:
        """Get custom curated list across all sectors."""
        return self._get_sp1000_tickers()

    def analyze_stock(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Analyze a single stock with error handling.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Analysis results or None if error
        """
        try:
            # Fetch data
            info = self.fetcher.get_stock_info(ticker)
            if not info:
                return None

            price_data = self.fetcher.get_price_history(ticker, period="1y")
            if price_data is None or price_data.empty:
                return None

            # Perform analysis
            momentum_analyzer = MomentumAnalyzer(price_data)
            momentum_analysis = momentum_analyzer.get_momentum_score()

            fundamental_analyzer = FundamentalAnalyzer(info)
            fundamental_analysis = fundamental_analyzer.get_fundamental_score()

            # Calculate composite score
            scorer = CompositeScorer(momentum_analysis, fundamental_analysis)
            composite = scorer.calculate_composite_score()

            return {
                'ticker': ticker,
                'company_name': info.get('longName', ticker),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'market_cap': info.get('marketCap'),
                'current_price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'composite_score': composite['composite_score'],
                'momentum_score': composite['momentum_score'],
                'fundamental_score': composite['fundamental_score'],
                'recommendation': composite['recommendation'],
                'investment_style': composite['investment_style'],
                'confidence': composite['confidence']
            }

        except Exception as e:
            print(f"Error analyzing {ticker}: {e}")
            return None

    def analyze_universe(self, tickers: List[str], max_stocks: Optional[int] = None) -> List[Dict[str, Any]]:
        """Analyze a universe of stocks.

        Args:
            tickers: List of ticker symbols
            max_stocks: Maximum number of stocks to analyze (None for all)

        Returns:
            List of analysis results
        """
        if max_stocks:
            tickers = tickers[:max_stocks]

        total = len(tickers)
        self.results = []

        print(f"\n🔍 Analyzing {total} stocks...\n")

        for i, ticker in enumerate(tickers, 1):
            print(f"[{i}/{total}] Analyzing {ticker}...", end=' ')

            result = self.analyze_stock(ticker)

            if result:
                self.results.append(result)
                score = result['composite_score']
                rec = result['recommendation']
                print(f"✓ Score: {score:.1f} ({rec})")
            else:
                print("✗ Failed")

            # Rate limiting
            if i < total:
                time.sleep(self.delay)

        print(f"\n✅ Successfully analyzed {len(self.results)} out of {total} stocks\n")
        return self.results

    def get_top_stocks(self, n: int = 20, min_score: float = 0) -> pd.DataFrame:
        """Get top N stocks by composite score.

        Args:
            n: Number of top stocks to return
            min_score: Minimum composite score threshold

        Returns:
            DataFrame with top stocks
        """
        df = pd.DataFrame(self.results)

        if df.empty:
            return df

        # Filter by minimum score
        df = df[df['composite_score'] >= min_score]

        # Sort by composite score
        df = df.sort_values('composite_score', ascending=False).head(n)

        return df

    def get_best_by_sector(self, n_per_sector: int = 3) -> pd.DataFrame:
        """Get best stocks in each sector.

        Args:
            n_per_sector: Number of stocks per sector

        Returns:
            DataFrame with best stocks by sector
        """
        df = pd.DataFrame(self.results)

        if df.empty:
            return df

        # Get top N stocks per sector
        top_by_sector = df.groupby('sector').apply(
            lambda x: x.nlargest(n_per_sector, 'composite_score')
        ).reset_index(drop=True)

        return top_by_sector.sort_values(['sector', 'composite_score'], ascending=[True, False])

    def get_investment_opportunities(self) -> Dict[str, pd.DataFrame]:
        """Categorize stocks by investment style.

        Returns:
            Dictionary of DataFrames by investment type
        """
        df = pd.DataFrame(self.results)

        if df.empty:
            return {}

        opportunities = {
            'Strong Buys': df[df['recommendation'] == 'Strong Buy'].sort_values('composite_score', ascending=False),
            'Momentum Plays': df[df['momentum_score'] >= 75].sort_values('momentum_score', ascending=False),
            'Value Plays': df[df['fundamental_score'] >= 75].sort_values('fundamental_score', ascending=False),
            'Balanced Growth': df[
                (df['momentum_score'] >= 70) & (df['fundamental_score'] >= 70)
            ].sort_values('composite_score', ascending=False),
            'High Conviction': df[
                df['confidence'].str.contains('High', na=False)
            ].sort_values('composite_score', ascending=False)
        }

        return opportunities

    def save_results(self, filename: str = None):
        """Save results to JSON and CSV files.

        Args:
            filename: Base filename (without extension)
        """
        if not self.results:
            print("No results to save")
            return

        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"stock_analysis_{timestamp}"

        # Save full results to JSON
        json_file = f"{filename}.json"
        with open(json_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"✓ Saved full results to {json_file}")

        # Save summary to CSV
        df = pd.DataFrame(self.results)
        csv_file = f"{filename}.csv"
        df.to_csv(csv_file, index=False)
        print(f"✓ Saved summary to {csv_file}")

        # Save top stocks to separate CSV
        top_stocks = self.get_top_stocks(50)
        if not top_stocks.empty:
            top_file = f"{filename}_top50.csv"
            top_stocks.to_csv(top_file, index=False)
            print(f"✓ Saved top 50 stocks to {top_file}")

    def print_summary(self):
        """Print analysis summary."""
        if not self.results:
            print("No results to summarize")
            return

        df = pd.DataFrame(self.results)

        self.formatter.console.print("\n" + "="*80)
        self.formatter.console.print("[bold cyan]📊 BATCH ANALYSIS SUMMARY[/bold cyan]")
        self.formatter.console.print("="*80 + "\n")

        # Overall statistics
        self.formatter.console.print(f"[bold]Total Stocks Analyzed:[/bold] {len(df)}")
        self.formatter.console.print(f"[bold]Average Composite Score:[/bold] {df['composite_score'].mean():.2f}")
        self.formatter.console.print(f"[bold]Average Momentum Score:[/bold] {df['momentum_score'].mean():.2f}")
        self.formatter.console.print(f"[bold]Average Fundamental Score:[/bold] {df['fundamental_score'].mean():.2f}\n")

        # Recommendation breakdown
        rec_counts = df['recommendation'].value_counts()
        self.formatter.console.print("[bold]Recommendations Breakdown:[/bold]")
        for rec, count in rec_counts.items():
            pct = (count / len(df)) * 100
            self.formatter.console.print(f"  {rec}: {count} ({pct:.1f}%)")

        # Top 20 stocks
        print("\n" + "="*80)
        self.formatter.console.print("[bold green]🏆 TOP 20 STOCKS[/bold green]")
        print("="*80 + "\n")

        top_20 = self.get_top_stocks(20)
        self.formatter.print_comparison_table([
            {'ticker': row['ticker'], 'analysis': {
                'composite_analysis': {
                    'composite_score': row['composite_score'],
                    'momentum_score': row['momentum_score'],
                    'fundamental_score': row['fundamental_score'],
                    'recommendation': row['recommendation'],
                    'investment_style': row['investment_style']
                }
            }} for _, row in top_20.iterrows()
        ])

        # Best by sector
        print("\n" + "="*80)
        self.formatter.console.print("[bold magenta]🎯 BEST STOCKS BY SECTOR[/bold magenta]")
        print("="*80 + "\n")

        by_sector = self.get_best_by_sector(3)
        current_sector = None
        for _, row in by_sector.iterrows():
            if row['sector'] != current_sector:
                current_sector = row['sector']
                self.formatter.console.print(f"\n[bold cyan]{current_sector}[/bold cyan]")

            color = self.formatter._get_score_color(row['composite_score'])
            self.formatter.console.print(
                f"  {row['ticker']:6} - {row['company_name'][:40]:40} | "
                f"[{color}]{row['composite_score']:.1f}[/{color}] | "
                f"{row['recommendation']}"
            )

        # Investment opportunities
        print("\n" + "="*80)
        self.formatter.console.print("[bold yellow]💡 INVESTMENT OPPORTUNITIES[/bold yellow]")
        print("="*80 + "\n")

        opportunities = self.get_investment_opportunities()

        for category, stocks in opportunities.items():
            if not stocks.empty:
                self.formatter.console.print(f"\n[bold]{category}:[/bold] {len(stocks)} stocks")
                for _, row in stocks.head(5).iterrows():
                    color = self.formatter._get_score_color(row['composite_score'])
                    self.formatter.console.print(
                        f"  {row['ticker']:6} - [{color}]{row['composite_score']:.1f}[/{color}] | "
                        f"M:{row['momentum_score']:.0f} F:{row['fundamental_score']:.0f}"
                    )


def main():
    """Main entry point for batch analyzer."""
    import argparse

    parser = argparse.ArgumentParser(description='Batch Stock Analyzer - Analyze large universes of stocks')
    parser.add_argument('--universe', choices=['sp500', 'sp1000', 'nasdaq100', 'custom'],
                        default='sp500', help='Stock universe to analyze')
    parser.add_argument('--max-stocks', type=int, help='Maximum number of stocks to analyze')
    parser.add_argument('--delay', type=float, default=0.5, help='Delay between API calls (seconds)')
    parser.add_argument('--min-score', type=float, default=0, help='Minimum composite score threshold')
    parser.add_argument('--no-cache', action='store_true', help='Disable caching')
    parser.add_argument('--output', help='Output filename (without extension)')

    args = parser.parse_args()

    # Initialize analyzer
    analyzer = BatchStockAnalyzer(use_cache=not args.no_cache, delay=args.delay)

    # Get stock universe
    tickers = analyzer.get_stock_universe(args.universe)
    print(f"📋 Selected {args.universe.upper()} universe: {len(tickers)} stocks")

    # Analyze stocks
    analyzer.analyze_universe(tickers, max_stocks=args.max_stocks)

    # Print summary
    analyzer.print_summary()

    # Save results
    analyzer.save_results(args.output)

    print("\n✅ Analysis complete!")


if __name__ == '__main__':
    main()
