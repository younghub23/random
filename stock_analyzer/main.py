#!/usr/bin/env python3
"""Main CLI entry point for the Stock Analyzer."""
import argparse
import sys
from typing import List, Optional

from data.fetcher import StockDataFetcher
from analysis.momentum import MomentumAnalyzer
from analysis.fundamental import FundamentalAnalyzer
from analysis.scoring import CompositeScorer
from utils.output import OutputFormatter
from utils.config import Config


class StockAnalyzer:
    """Main stock analyzer application."""

    def __init__(self, use_cache: bool = True):
        """Initialize the stock analyzer.

        Args:
            use_cache: Whether to use caching
        """
        self.fetcher = StockDataFetcher(use_cache=use_cache)
        self.formatter = OutputFormatter()

    def analyze_single_stock(self, ticker: str, detailed: bool = True) -> Optional[dict]:
        """Analyze a single stock.

        Args:
            ticker: Stock ticker symbol
            detailed: Whether to print detailed output

        Returns:
            Analysis results dictionary or None if error
        """
        ticker = ticker.upper()

        if detailed:
            self.formatter.console.print(f"\n[cyan]Analyzing {ticker}...[/cyan]")

        # Fetch data
        info = self.fetcher.get_stock_info(ticker)
        if not info:
            self.formatter.console.print(f"[red]Error: Could not fetch data for {ticker}[/red]")
            return None

        price_data = self.fetcher.get_price_history(ticker, period="1y")
        if price_data is None or price_data.empty:
            self.formatter.console.print(f"[red]Error: Could not fetch price history for {ticker}[/red]")
            return None

        # Perform momentum analysis
        momentum_analyzer = MomentumAnalyzer(price_data)
        momentum_analysis = momentum_analyzer.get_momentum_score()

        # Perform fundamental analysis
        fundamental_analyzer = FundamentalAnalyzer(info)
        fundamental_analysis = fundamental_analyzer.get_fundamental_score()

        # Calculate composite score
        scorer = CompositeScorer(momentum_analysis, fundamental_analysis)
        full_analysis = scorer.get_detailed_report()

        if detailed:
            self.formatter.print_full_analysis(ticker, info, full_analysis)

        return {
            'ticker': ticker,
            'info': info,
            'analysis': full_analysis
        }

    def compare_stocks(self, tickers: List[str]):
        """Compare multiple stocks.

        Args:
            tickers: List of ticker symbols
        """
        self.formatter.console.print(f"\n[cyan]Comparing {len(tickers)} stocks...[/cyan]\n")

        results = []
        for ticker in tickers:
            result = self.analyze_single_stock(ticker, detailed=False)
            if result:
                results.append(result)

        if results:
            self.formatter.print_comparison_table(results)

            # Print individual detailed analyses
            for result in results:
                self.formatter.console.print("\n" + "="*80 + "\n")
                self.formatter.print_full_analysis(
                    result['ticker'],
                    result['info'],
                    result['analysis']
                )
        else:
            self.formatter.console.print("[red]No valid stocks to compare[/red]")

    def screen_stocks(self, tickers: List[str], momentum_min: float = 0,
                     fundamental_min: float = 0, composite_min: float = 0):
        """Screen stocks based on criteria.

        Args:
            tickers: List of ticker symbols to screen
            momentum_min: Minimum momentum score
            fundamental_min: Minimum fundamental score
            composite_min: Minimum composite score
        """
        self.formatter.console.print(f"\n[cyan]Screening {len(tickers)} stocks...[/cyan]")
        self.formatter.console.print(f"Criteria: Momentum >= {momentum_min}, Fundamental >= {fundamental_min}, Composite >= {composite_min}\n")

        passing_stocks = []

        for ticker in tickers:
            result = self.analyze_single_stock(ticker, detailed=False)
            if result:
                composite = result['analysis']['composite_analysis']

                if (composite['momentum_score'] >= momentum_min and
                    composite['fundamental_score'] >= fundamental_min and
                    composite['composite_score'] >= composite_min):
                    passing_stocks.append(result)

        if passing_stocks:
            # Sort by composite score
            passing_stocks.sort(key=lambda x: x['analysis']['composite_analysis']['composite_score'], reverse=True)

            self.formatter.console.print(f"\n[green]Found {len(passing_stocks)} stocks meeting criteria:[/green]\n")
            self.formatter.print_comparison_table(passing_stocks)
        else:
            self.formatter.console.print("\n[yellow]No stocks met the screening criteria[/yellow]")

    def watchlist_monitor(self, tickers: List[str], alert_threshold: float = 75):
        """Monitor a watchlist of stocks.

        Args:
            tickers: List of ticker symbols
            alert_threshold: Score threshold for alerts
        """
        self.formatter.console.print(f"\n[cyan]Monitoring watchlist ({len(tickers)} stocks)...[/cyan]\n")

        results = []
        alerts = []

        for ticker in tickers:
            result = self.analyze_single_stock(ticker, detailed=False)
            if result:
                results.append(result)

                composite_score = result['analysis']['composite_analysis']['composite_score']
                if composite_score >= alert_threshold:
                    alerts.append(result)

        if results:
            self.formatter.print_comparison_table(results)

            if alerts:
                self.formatter.console.print(f"\n[yellow]⚠️  {len(alerts)} stocks above alert threshold ({alert_threshold}):[/yellow]")
                for alert in alerts:
                    ticker = alert['ticker']
                    score = alert['analysis']['composite_analysis']['composite_score']
                    recommendation = alert['analysis']['composite_analysis']['recommendation']
                    self.formatter.console.print(f"  • {ticker}: {score:.1f} - {recommendation}")
        else:
            self.formatter.console.print("[red]No valid stocks in watchlist[/red]")

    def clear_cache(self):
        """Clear all cached data."""
        self.fetcher.clear_cache()
        self.formatter.console.print("[green]Cache cleared successfully[/green]")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Stock Analyzer - Comprehensive momentum and fundamental analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s analyze AAPL
  %(prog)s compare AAPL MSFT GOOGL
  %(prog)s screen AAPL MSFT GOOGL TSLA --momentum-min 70 --composite-min 65
  %(prog)s watchlist AAPL MSFT NVDA --alert-threshold 80
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a single stock')
    analyze_parser.add_argument('ticker', help='Stock ticker symbol')
    analyze_parser.add_argument('--no-cache', action='store_true', help='Disable caching')
    analyze_parser.add_argument('--export', help='Export results to JSON file')

    # Compare command
    compare_parser = subparsers.add_parser('compare', help='Compare multiple stocks')
    compare_parser.add_argument('tickers', nargs='+', help='Stock ticker symbols')
    compare_parser.add_argument('--no-cache', action='store_true', help='Disable caching')

    # Screen command
    screen_parser = subparsers.add_parser('screen', help='Screen stocks by criteria')
    screen_parser.add_argument('tickers', nargs='+', help='Stock ticker symbols')
    screen_parser.add_argument('--momentum-min', type=float, default=0, help='Minimum momentum score')
    screen_parser.add_argument('--fundamental-min', type=float, default=0, help='Minimum fundamental score')
    screen_parser.add_argument('--composite-min', type=float, default=0, help='Minimum composite score')
    screen_parser.add_argument('--no-cache', action='store_true', help='Disable caching')

    # Watchlist command
    watchlist_parser = subparsers.add_parser('watchlist', help='Monitor a watchlist')
    watchlist_parser.add_argument('tickers', nargs='+', help='Stock ticker symbols')
    watchlist_parser.add_argument('--alert-threshold', type=float, default=75, help='Alert threshold score')
    watchlist_parser.add_argument('--no-cache', action='store_true', help='Disable caching')

    # Clear cache command
    cache_parser = subparsers.add_parser('clear-cache', help='Clear all cached data')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Initialize analyzer
    use_cache = not getattr(args, 'no_cache', False)
    analyzer = StockAnalyzer(use_cache=use_cache)

    # Execute command
    try:
        if args.command == 'analyze':
            result = analyzer.analyze_single_stock(args.ticker)
            if result and args.export:
                analyzer.formatter.export_to_json(result, args.export)

        elif args.command == 'compare':
            analyzer.compare_stocks(args.tickers)

        elif args.command == 'screen':
            analyzer.screen_stocks(
                args.tickers,
                momentum_min=args.momentum_min,
                fundamental_min=args.fundamental_min,
                composite_min=args.composite_min
            )

        elif args.command == 'watchlist':
            analyzer.watchlist_monitor(args.tickers, alert_threshold=args.alert_threshold)

        elif args.command == 'clear-cache':
            analyzer.clear_cache()

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
