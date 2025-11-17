"""Weight optimization system to find optimal weights for predictive accuracy.

This module runs simulations with different weight configurations to:
1. Find weights that maximize returns
2. Find weights that maximize Sharpe ratio (risk-adjusted returns)
3. Find weights that maximize win rate
4. Identify which metrics contribute most to predictive power
"""

import json
import itertools
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import pandas as pd
from pathlib import Path

from backtest import Backtester, WeightedScorer


class WeightOptimizer:
    """Optimize scoring weights for maximum predictive accuracy."""

    def __init__(self):
        """Initialize weight optimizer."""
        self.backtester = None
        self.results = []

    def generate_weight_combinations(self, parameters: List[str], granularity: int = 5) -> List[Dict[str, float]]:
        """Generate combinations of weights that sum to 1.0.

        Args:
            parameters: List of parameter names
            granularity: Number of steps (5 = 0.0, 0.2, 0.4, 0.6, 0.8, 1.0)

        Returns:
            List of weight dictionaries
        """
        # Generate values that sum to 1.0
        step = 1.0 / granularity
        values = [i * step for i in range(granularity + 1)]

        combinations = []

        # Generate all combinations that sum to 1.0
        for combo in itertools.product(values, repeat=len(parameters)):
            if abs(sum(combo) - 1.0) < 0.01:  # Allow small floating point errors
                weight_dict = dict(zip(parameters, combo))
                combinations.append(weight_dict)

        return combinations

    def test_weight_configuration(self, weights: Dict[str, Any], tickers: List[str],
                                 analysis_date: datetime, holding_period: int = 90,
                                 top_n: int = 10) -> Dict[str, Any]:
        """Test a specific weight configuration.

        Args:
            weights: Weight configuration dictionary
            tickers: List of stock tickers
            analysis_date: Date to analyze
            holding_period: Days to hold
            top_n: Number of stocks to select

        Returns:
            Performance metrics
        """
        # Create temporary weights file
        temp_weights_file = 'temp_weights.json'

        with open(temp_weights_file, 'w') as f:
            json.dump(weights, f)

        # Initialize backtester with these weights
        backtester = Backtester(weights_file=temp_weights_file)

        # Run backtest
        result = backtester.backtest_portfolio(tickers, analysis_date, holding_period, top_n)

        # Clean up temp file
        Path(temp_weights_file).unlink()

        return result

    def optimize_composite_weights(self, tickers: List[str], analysis_date: datetime,
                                  holding_period: int = 90, granularity: int = 5) -> Dict[str, Any]:
        """Optimize top-level composite weights (momentum vs fundamental vs sentiment).

        Args:
            tickers: List of stock tickers to test on
            analysis_date: Date to analyze
            holding_period: Holding period in days
            granularity: Number of weight steps to test

        Returns:
            Dictionary with optimization results
        """
        print("\n🔍 Optimizing Composite Weights (Momentum vs Fundamental vs Sentiment)")
        print("="*80)

        # Generate weight combinations
        parameters = ['momentum', 'fundamental', 'sentiment']
        combinations = self.generate_weight_combinations(parameters, granularity)

        print(f"Testing {len(combinations)} weight combinations...")

        results = []

        for i, combo in enumerate(combinations, 1):
            # Create full weights config
            weights_config = {
                'composite_weights': combo,
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

            # Test this configuration
            try:
                performance = self.test_weight_configuration(
                    weights_config, tickers, analysis_date, holding_period
                )

                if performance:
                    result = {
                        'weights': combo,
                        'avg_return': performance.get('avg_return', 0),
                        'sharpe_ratio': performance.get('sharpe_ratio', 0),
                        'win_rate': performance.get('win_rate', 0),
                        'std_return': performance.get('std_return', 0)
                    }
                    results.append(result)

                    print(f"[{i}/{len(combinations)}] M:{combo['momentum']:.2f} F:{combo['fundamental']:.2f} S:{combo['sentiment']:.2f} "
                          f"→ Return:{result['avg_return']:.2f}% Sharpe:{result['sharpe_ratio']:.2f}")

            except Exception as e:
                print(f"Error testing combination {i}: {e}")

        # Find best configurations
        if results:
            best_return = max(results, key=lambda x: x['avg_return'])
            best_sharpe = max(results, key=lambda x: x['sharpe_ratio'])
            best_win_rate = max(results, key=lambda x: x['win_rate'])

            return {
                'tested_combinations': len(results),
                'best_return': best_return,
                'best_sharpe': best_sharpe,
                'best_win_rate': best_win_rate,
                'all_results': results
            }

        return {}

    def optimize_momentum_weights(self, tickers: List[str], analysis_date: datetime,
                                 holding_period: int = 90, granularity: int = 3) -> Dict[str, Any]:
        """Optimize individual momentum indicator weights.

        Args:
            tickers: List of stock tickers to test on
            analysis_date: Date to analyze
            holding_period: Holding period in days
            granularity: Number of weight steps (lower due to 6 parameters)

        Returns:
            Dictionary with optimization results
        """
        print("\n🔍 Optimizing Momentum Indicator Weights")
        print("="*80)

        # Generate weight combinations (6 parameters - use lower granularity)
        parameters = ['moving_averages', 'rsi', 'macd', 'volume', 'price_momentum', 'trend_strength']
        combinations = self.generate_weight_combinations(parameters, granularity)

        print(f"Testing {len(combinations)} weight combinations...")

        results = []

        for i, combo in enumerate(combinations, 1):
            # Create full weights config with this momentum configuration
            weights_config = {
                'composite_weights': {
                    'momentum': 0.40,
                    'fundamental': 0.50,
                    'sentiment': 0.10
                },
                'momentum_weights': combo,
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

            # Test this configuration
            try:
                performance = self.test_weight_configuration(
                    weights_config, tickers, analysis_date, holding_period
                )

                if performance:
                    result = {
                        'weights': combo,
                        'avg_return': performance.get('avg_return', 0),
                        'sharpe_ratio': performance.get('sharpe_ratio', 0),
                        'win_rate': performance.get('win_rate', 0)
                    }
                    results.append(result)

                    if i % 50 == 0:
                        print(f"[{i}/{len(combinations)}] Tested... Best so far: {max(results, key=lambda x: x['avg_return'])['avg_return']:.2f}%")

            except Exception as e:
                if i % 100 == 0:
                    print(f"Progress: {i}/{len(combinations)}")

        # Find best configuration
        if results:
            best_return = max(results, key=lambda x: x['avg_return'])

            print("\n✅ Best Momentum Weights Found:")
            for param, weight in best_return['weights'].items():
                print(f"  {param:20} {weight:.2f}")
            print(f"\nAverage Return: {best_return['avg_return']:.2f}%")
            print(f"Sharpe Ratio: {best_return['sharpe_ratio']:.2f}")

            return {
                'tested_combinations': len(results),
                'best_configuration': best_return,
                'all_results': results
            }

        return {}

    def grid_search_top_weights(self, tickers: List[str], analysis_date: datetime,
                               holding_period: int = 90) -> pd.DataFrame:
        """Perform grid search on composite weights with fine granularity.

        Args:
            tickers: List of stock tickers
            analysis_date: Analysis date
            holding_period: Holding period in days

        Returns:
            DataFrame with all tested configurations
        """
        print("\n🔍 Grid Search: Momentum vs Fundamental vs Sentiment Weights")
        print("="*80)

        results = []

        # Test various combinations
        momentum_values = [0.2, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6]
        fundamental_values = [0.3, 0.4, 0.5, 0.6, 0.7]

        total_combos = len(momentum_values) * len(fundamental_values)
        tested = 0

        for momentum_weight in momentum_values:
            for fundamental_weight in fundamental_values:
                # Sentiment gets the remainder
                sentiment_weight = 1.0 - momentum_weight - fundamental_weight

                if sentiment_weight < 0 or sentiment_weight > 0.3:
                    continue

                tested += 1
                print(f"[{tested}/{total_combos}] Testing M:{momentum_weight:.2f} F:{fundamental_weight:.2f} S:{sentiment_weight:.2f}...",
                      end=' ')

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

                try:
                    performance = self.test_weight_configuration(
                        weights_config, tickers, analysis_date, holding_period
                    )

                    if performance:
                        results.append({
                            'momentum_weight': momentum_weight,
                            'fundamental_weight': fundamental_weight,
                            'sentiment_weight': sentiment_weight,
                            'avg_return': performance.get('avg_return', 0),
                            'median_return': performance.get('median_return', 0),
                            'std_return': performance.get('std_return', 0),
                            'sharpe_ratio': performance.get('sharpe_ratio', 0),
                            'win_rate': performance.get('win_rate', 0)
                        })

                        print(f"Return: {performance.get('avg_return', 0):.2f}% Sharpe: {performance.get('sharpe_ratio', 0):.2f}")
                    else:
                        print("Failed")

                except Exception as e:
                    print(f"Error: {e}")

        df = pd.DataFrame(results)

        if not df.empty:
            # Sort by average return
            df = df.sort_values('avg_return', ascending=False)

            print("\n" + "="*80)
            print("Top 10 Weight Configurations")
            print("="*80)
            print(df.head(10).to_string(index=False))

            # Save results
            output_file = f"weight_optimization_{analysis_date.strftime('%Y%m%d')}.csv"
            df.to_csv(output_file, index=False)
            print(f"\n✓ Results saved to {output_file}")

        return df


def main():
    """Main entry point for weight optimization."""
    import argparse

    parser = argparse.ArgumentParser(description='Optimize Stock Analysis Weights')
    parser.add_argument('--tickers', nargs='+', required=True, help='List of tickers to test on')
    parser.add_argument('--date', required=True, help='Analysis date (YYYY-MM-DD)')
    parser.add_argument('--holding-period', type=int, default=90, help='Holding period in days')
    parser.add_argument('--mode', choices=['composite', 'momentum', 'grid'], default='grid',
                       help='Optimization mode')
    parser.add_argument('--granularity', type=int, default=5, help='Weight granularity for composite/momentum')

    args = parser.parse_args()

    # Parse date
    analysis_date = datetime.strptime(args.date, '%Y-%m-%d')

    # Initialize optimizer
    optimizer = WeightOptimizer()

    if args.mode == 'composite':
        results = optimizer.optimize_composite_weights(
            args.tickers, analysis_date, args.holding_period, args.granularity
        )

        if results:
            print("\n" + "="*80)
            print("OPTIMIZATION RESULTS")
            print("="*80)

            print("\n🏆 Best Configuration by Average Return:")
            for param, weight in results['best_return']['weights'].items():
                print(f"  {param:20} {weight:.2f}")
            print(f"  Average Return: {results['best_return']['avg_return']:.2f}%")

            print("\n📊 Best Configuration by Sharpe Ratio:")
            for param, weight in results['best_sharpe']['weights'].items():
                print(f"  {param:20} {weight:.2f}")
            print(f"  Sharpe Ratio: {results['best_sharpe']['sharpe_ratio']:.2f}")

    elif args.mode == 'momentum':
        results = optimizer.optimize_momentum_weights(
            args.tickers, analysis_date, args.holding_period, args.granularity
        )

    elif args.mode == 'grid':
        df = optimizer.grid_search_top_weights(
            args.tickers, analysis_date, args.holding_period
        )


if __name__ == '__main__':
    main()
