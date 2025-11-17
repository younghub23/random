#!/usr/bin/env python3
"""Demo script to show backtesting with sample data (no API calls needed)."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

print("\n" + "="*80)
print("BACKTESTING DEMO - Using Sample Data")
print("="*80 + "\n")

# Generate sample stock data
dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
np.random.seed(42)

# Simulate AAPL price movement
base_price = 150
price_changes = np.random.normal(0.001, 0.02, len(dates))
prices = base_price * np.exp(np.cumsum(price_changes))

# Create sample data
sample_data = pd.DataFrame({
    'Date': dates,
    'Close': prices,
    'High': prices * 1.01,
    'Low': prices * 0.99,
    'Volume': np.random.randint(50000000, 150000000, len(dates))
})

print("Sample AAPL Stock Data (First 5 days):")
print(sample_data.head())
print("\n")

# Simulate momentum analysis
print("MOMENTUM ANALYSIS SIMULATION")
print("-" * 80)

momentum_components = {
    'moving_averages': 18,  # out of 20
    'rsi': 13,             # out of 15
    'macd': 12,            # out of 15
    'volume': 11,          # out of 15
    'price_momentum': 17,  # out of 20
    'trend_strength': 12   # out of 15
}

print("Component Scores:")
for component, score in momentum_components.items():
    print(f"  {component:20} {score}/20")

total_momentum = sum(momentum_components.values())
print(f"\nTotal Momentum Score: {total_momentum}/100")

# Simulate fundamental analysis
print("\n" + "="*80)
print("FUNDAMENTAL ANALYSIS SIMULATION")
print("-" * 80)

fundamental_components = {
    'valuation': 20,        # out of 25
    'profitability': 23,    # out of 25
    'financial_health': 22, # out of 25
    'growth': 21           # out of 25
}

print("Component Scores:")
for component, score in fundamental_components.items():
    print(f"  {component:20} {score}/25")

total_fundamental = sum(fundamental_components.values())
print(f"\nTotal Fundamental Score: {total_fundamental}/100")

# Load weights
print("\n" + "="*80)
print("WEIGHTED SCORING")
print("-" * 80)

weights = {
    'composite_weights': {
        'momentum': 0.35,
        'fundamental': 0.50,
        'sentiment': 0.15
    }
}

sentiment_score = 75  # Sample sentiment

composite_score = (
    total_momentum * weights['composite_weights']['momentum'] +
    total_fundamental * weights['composite_weights']['fundamental'] +
    sentiment_score * weights['composite_weights']['sentiment']
)

print(f"Weights: Momentum={weights['composite_weights']['momentum']}, "
      f"Fundamental={weights['composite_weights']['fundamental']}, "
      f"Sentiment={weights['composite_weights']['sentiment']}")
print(f"\nWeighted Contributions:")
print(f"  Momentum:    {total_momentum} × {weights['composite_weights']['momentum']} = {total_momentum * weights['composite_weights']['momentum']:.2f}")
print(f"  Fundamental: {total_fundamental} × {weights['composite_weights']['fundamental']} = {total_fundamental * weights['composite_weights']['fundamental']:.2f}")
print(f"  Sentiment:   {sentiment_score} × {weights['composite_weights']['sentiment']} = {sentiment_score * weights['composite_weights']['sentiment']:.2f}")
print(f"\nComposite Score: {composite_score:.2f}/100")

# Simulate returns
print("\n" + "="*80)
print("BACKTESTING SIMULATION")
print("-" * 80)

# Simulate that we analyzed at multiple dates
analysis_dates = pd.date_range(start='2023-06-01', end='2023-12-01', freq='M')
holding_period = 90

results = []
for i, date in enumerate(analysis_dates):
    # Simulate score with some variation
    score = composite_score + np.random.normal(0, 5)

    # Simulate future return (higher scores → higher returns, with noise)
    expected_return = (score - 50) * 0.5  # Base relationship
    actual_return = expected_return + np.random.normal(0, 10)

    results.append({
        'date': date.strftime('%Y-%m-%d'),
        'score': round(score, 2),
        'actual_return': round(actual_return, 2)
    })

results_df = pd.DataFrame(results)

print("\nBacktest Results:")
print(results_df.to_string(index=False))

# Calculate correlation
correlation = results_df['score'].corr(results_df['actual_return'])

print(f"\n{'='*80}")
print("METRIC IMPORTANCE ANALYSIS")
print("="*80)

print(f"\nCorrelation between Score and Actual Return: {correlation:+.3f}")

if correlation > 0.5:
    print("✓ Strong positive correlation - high scores predict high returns!")
elif correlation > 0.3:
    print("✓ Moderate correlation - scores have predictive power")
else:
    print("⚠ Weak correlation - model needs optimization")

print("\nComponent Correlations (simulated):")
component_correlations = {
    'price_momentum': 0.687,
    'moving_averages': 0.542,
    'trend_strength': 0.421,
    'growth': 0.384,
    'profitability': 0.312,
    'rsi': 0.234,
    'macd': 0.189,
    'volume': 0.156
}

for component, corr in sorted(component_correlations.items(), key=lambda x: abs(x[1]), reverse=True):
    indicator = "🟢" if abs(corr) > 0.4 else "🟡" if abs(corr) > 0.2 else "🔴"
    print(f"{indicator} {component:25} {corr:+.3f}")

print("\n" + "="*80)
print("INTERPRETATION")
print("="*80)

print("""
This demo shows:

1. How each metric contributes to the final score
2. How weights affect the composite score
3. How backtesting validates predictive power
4. Which metrics are most important (via correlation)

To run with real data:
- Wait for Yahoo Finance API to be accessible
- Try at a different time of day
- Use --no-cache flag for fresh data
- Consider using a VPN if blocked

Current Yahoo Finance Status: BLOCKED (403 errors)
Recommendation: Try again in 15-30 minutes
""")

print("="*80)
