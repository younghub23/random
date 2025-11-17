# Backtesting & Weight Optimization Guide

This guide explains how to validate the predictive power of the stock scoring model and optimize weights for maximum accuracy.

## Overview

The stock analyzer now includes three powerful tools:

1. **Backtesting** (`backtest.py`) - Test historical performance
2. **Weight Optimization** (`optimize_weights.py`) - Find optimal weights
3. **Sentiment Analysis** (`analysis/sentiment.py`) - Add news sentiment scoring

## Quick Start

### 1. Backtest a Single Stock

Test if high scores actually predict future returns:

```bash
python backtest.py \
  --ticker AAPL \
  --start-date 2023-01-01 \
  --end-date 2024-01-01 \
  --holding-period 90
```

**Output:**
- Correlation of each metric with future returns
- Shows which indicators are most predictive

### 2. Backtest a Portfolio Strategy

Test portfolio selection at a specific date:

```bash
python backtest.py \
  --tickers AAPL MSFT GOOGL NVDA TSLA META AMZN NFLX \
  --start-date 2023-06-01 \
  --holding-period 90 \
  --top-n 5
```

**Output:**
- Selected top 5 stocks based on scores
- Actual returns over 90 days
- Portfolio metrics (Sharpe ratio, win rate, etc.)

### 3. Optimize Weights

Find the best weight configuration:

```bash
python optimize_weights.py \
  --tickers AAPL MSFT GOOGL NVDA TSLA META AMZN NFLX ADBE CRM \
  --date 2023-06-01 \
  --holding-period 90 \
  --mode grid
```

**Output:**
- Tests different weight combinations
- Ranks by return, Sharpe ratio, win rate
- Saves results to CSV

---

## Understanding the Scoring System

### Composite Score Formula

```
Composite Score = (Momentum × M_weight) + (Fundamental × F_weight) + (Sentiment × S_weight)
```

**Default Weights:**
- Momentum: 35%
- Fundamental: 50%
- Sentiment: 15%

### Momentum Components (35% of total)

| Component | Weight | Max Points | Description |
|-----------|--------|------------|-------------|
| Moving Averages | 20% | 20 | Price vs 20/50/200-day MAs |
| RSI | 15% | 15 | Overbought/oversold detection |
| MACD | 15% | 15 | Trend direction signals |
| Volume | 15% | 15 | Volume trends & price correlation |
| Price Momentum | 20% | 20 | Multi-period returns |
| Trend Strength | 15% | 15 | ADX trend strength |

**Example Calculation:**
```
MA Score: 18/20 → Normalized: (18/20) * 100 = 90
Weighted: 90 * 0.20 = 18 points (out of 100)

Total Momentum = Sum of all weighted components
```

### Fundamental Components (50% of total)

| Component | Weight | Max Points | Description |
|-----------|--------|------------|-------------|
| Valuation | 25% | 25 | P/E, PEG, P/B ratios |
| Profitability | 25% | 25 | Margins, ROE, ROA |
| Financial Health | 25% | 25 | Debt, liquidity, cash flow |
| Growth | 25% | 25 | Revenue & earnings growth |

### Sentiment Components (15% of total)

| Component | Weight | Description |
|-----------|--------|-------------|
| Base Sentiment | 70% | Direct sentiment from headlines |
| Positive Ratio | 20% | % of positive headlines |
| Headline Volume | 10% | News attention level |

---

## Configuring Weights

### Edit `weights_config.json`

```json
{
  "composite_weights": {
    "momentum": 0.35,      // ← Adjust these
    "fundamental": 0.50,   // ← Adjust these
    "sentiment": 0.15      // ← Adjust these
  },

  "momentum_weights": {
    "moving_averages": 0.20,  // ← Fine-tune individual indicators
    "rsi": 0.15,
    "macd": 0.15,
    "volume": 0.15,
    "price_momentum": 0.20,
    "trend_strength": 0.15
  },

  "fundamental_weights": {
    "valuation": 0.25,         // ← Fine-tune individual metrics
    "profitability": 0.25,
    "financial_health": 0.25,
    "growth": 0.25
  }
}
```

**Rules:**
- Each section must sum to 1.0
- Use decimals (0.25 = 25%)
- Higher weight = more important

---

## Backtesting Examples

### Example 1: Test Single Stock Over Time

```bash
python backtest.py \
  --ticker AAPL \
  --start-date 2022-01-01 \
  --end-date 2023-12-31 \
  --holding-period 180
```

**What it does:**
- Analyzes AAPL monthly from Jan 2022 - Dec 2023
- Calculates score at each date
- Measures actual 180-day returns
- Shows correlation: score vs. actual return

**Use case:** Validate if the model correctly identifies good entry points

### Example 2: Test Portfolio Selection Strategy

```bash
python backtest.py \
  --tickers AAPL MSFT GOOGL AMZN NVDA META TSLA NFLX ADBE CRM ORCL INTC AMD QCOM CSCO \
  --start-date 2023-01-01 \
  --holding-period 90 \
  --top-n 10
```

**What it does:**
- Analyzes all 15 stocks on Jan 1, 2023
- Selects top 10 by composite score
- Calculates actual 90-day returns
- Reports portfolio metrics

**Use case:** Backtest if picking top-scored stocks outperforms

### Example 3: Metric Importance Analysis

```bash
python backtest.py \
  --ticker NVDA \
  --start-date 2022-01-01 \
  --end-date 2023-12-31 \
  --holding-period 90
```

**Output shows:**
```
Metric Correlation with Future Returns
==========================================
price_momentum                           +0.687  ← Most predictive!
moving_averages                          +0.542
trend_strength                           +0.421
fundamental_growth                       +0.384
rsi                                      +0.234
...
```

**Interpretation:**
- Positive correlation = higher score → higher returns
- Larger absolute value = stronger relationship
- Use this to adjust weights!

---

## Weight Optimization

### Optimization Modes

#### 1. Grid Search (Recommended for beginners)

Tests comprehensive combinations of composite weights:

```bash
python optimize_weights.py \
  --tickers AAPL MSFT GOOGL NVDA TSLA META AMZN NFLX \
  --date 2023-06-01 \
  --mode grid
```

**Tests:**
- Momentum: 20%, 30%, 35%, 40%, 45%, 50%, 60%
- Fundamental: 30%, 40%, 50%, 60%, 70%
- Sentiment: Remainder (up to 30%)

**Output:** CSV with all combinations ranked by return

#### 2. Composite Optimization

Fine-grained search of composite weights:

```bash
python optimize_weights.py \
  --tickers AAPL MSFT GOOGL NVDA TSLA \
  --date 2023-06-01 \
  --mode composite \
  --granularity 5
```

**Granularity:**
- 5 = tests 0.0, 0.2, 0.4, 0.6, 0.8, 1.0
- 10 = tests 0.0, 0.1, 0.2, ..., 1.0 (more combos)

#### 3. Momentum Indicator Optimization

Optimize individual momentum indicators:

```bash
python optimize_weights.py \
  --tickers AAPL MSFT GOOGL NVDA TSLA \
  --date 2023-06-01 \
  --mode momentum \
  --granularity 3
```

**Warning:** 6 parameters with granularity 3 = 56 combinations
Use lower granularity to avoid very long runtimes

---

## Workflow: Optimize Your Model

### Step 1: Baseline Test

Run backtest with default weights:

```bash
python backtest.py \
  --tickers AAPL MSFT GOOGL NVDA TSLA META AMZN NFLX ADBE CRM \
  --start-date 2023-01-01 \
  --holding-period 90 \
  --top-n 5
```

**Record:** Average return, Sharpe ratio, win rate

### Step 2: Optimize Composite Weights

```bash
python optimize_weights.py \
  --tickers AAPL MSFT GOOGL NVDA TSLA META AMZN NFLX ADBE CRM \
  --date 2023-01-01 \
  --mode grid
```

**Result:** CSV file with optimal weights

### Step 3: Update Configuration

Edit `weights_config.json` with winning weights:

```json
{
  "composite_weights": {
    "momentum": 0.45,      // ← From optimization
    "fundamental": 0.45,   // ← From optimization
    "sentiment": 0.10      // ← From optimization
  }
}
```

### Step 4: Validate Improvement

Re-run backtest with new weights:

```bash
python backtest.py \
  --tickers AAPL MSFT GOOGL NVDA TSLA META AMZN NFLX ADBE CRM \
  --start-date 2023-01-01 \
  --holding-period 90 \
  --top-n 5 \
  --weights weights_config.json
```

**Compare:** Did average return improve?

### Step 5: Test on Different Periods

Validate on different time periods to avoid overfitting:

```bash
# Test on Q2 2023
python backtest.py --tickers ... --start-date 2023-04-01 --weights weights_config.json

# Test on Q3 2023
python backtest.py --tickers ... --start-date 2023-07-01 --weights weights_config.json

# Test on Q4 2023
python backtest.py --tickers ... --start-date 2023-10-01 --weights weights_config.json
```

If it performs well across different periods → weights are robust!

---

## Sentiment Analysis

### How It Works

The sentiment analyzer:

1. **Fetches recent news** from Google News and Yahoo Finance
2. **Analyzes headlines** using sentiment word matching
3. **Calculates score** based on positive/negative word ratio
4. **Weights by volume** - more news = more market attention

### Sentiment Scoring

```python
# Example headline analysis

"Apple beats earnings expectations, stock surges"
→ Positive words: beats, surges
→ Negative words: none
→ Sentiment: 100/100 (Very Positive)

"Tesla misses delivery targets amid growing concerns"
→ Positive words: growing
→ Negative words: misses, concerns
→ Sentiment: 25/100 (Negative)
```

### Using Sentiment in Scoring

Sentiment is weighted at 15% by default:

```
Final Score = (Momentum × 0.35) + (Fundamental × 0.50) + (Sentiment × 0.15)
```

**Example:**
- Momentum: 75
- Fundamental: 80
- Sentiment: 90 (very positive news)

```
Score = (75 × 0.35) + (80 × 0.50) + (90 × 0.15)
      = 26.25 + 40 + 13.5
      = 79.75 → "Buy" recommendation
```

### Adjusting Sentiment Weight

If backtesting shows sentiment is highly predictive, increase its weight:

```json
{
  "composite_weights": {
    "momentum": 0.30,
    "fundamental": 0.50,
    "sentiment": 0.20    // ← Increased from 0.15
  }
}
```

---

## Performance Metrics Explained

### Average Return
- Mean return across all selected stocks
- Higher is better
- **Goal:** Beat market benchmark (S&P 500 ~10% annual)

### Median Return
- Middle value of returns
- Less affected by outliers
- More stable metric than average

### Sharpe Ratio
- Risk-adjusted return: `(Return - RiskFree) / StdDev`
- Measures return per unit of risk
- **Interpretation:**
  - < 1.0 = Poor risk-adjusted returns
  - 1.0 - 2.0 = Good
  - \> 2.0 = Excellent

### Win Rate
- Percentage of stocks with positive returns
- **Interpretation:**
  - > 60% = Good stock picking
  - > 70% = Excellent
  - > 80% = Outstanding

### Standard Deviation
- Volatility of returns
- Lower is better (more consistent)
- Used to calculate Sharpe ratio

---

## Tips for Effective Backtesting

### 1. Use Sufficient Data
- Test on at least 10-20 stocks
- Test multiple time periods
- Avoid cherry-picking dates that work

### 2. Avoid Overfitting
- Don't optimize on a single date/period
- Validate on out-of-sample data
- Keep it simple - fewer parameters is better

### 3. Consider Market Conditions
- Bull market (2023) vs Bear market (2022)
- Sector rotation effects
- Macro economic factors

### 4. Holding Period Matters
- Short-term (30-90 days) = momentum more important
- Long-term (180-365 days) = fundamentals more important
- Match weights to your investment horizon

### 5. Compare to Benchmark
- Always compare to S&P 500 returns
- Goal: Outperform with similar or lower risk
- Consider transaction costs in real trading

---

## Common Use Cases

### Case 1: Growth Investor

**Preference:** High-growth tech stocks

**Optimize for:**
```bash
python optimize_weights.py \
  --tickers NVDA TSLA META AMZN NFLX SHOP SQ ROKU \
  --date 2023-06-01 \
  --mode grid
```

**Likely result:** Higher momentum weight (0.40-0.50)

### Case 2: Value Investor

**Preference:** Undervalued stable companies

**Optimize for:**
```bash
python optimize_weights.py \
  --tickers JNJ PG KO WMT XOM CVX UNH \
  --date 2023-06-01 \
  --mode grid
```

**Likely result:** Higher fundamental weight (0.60-0.70)

### Case 3: Balanced Portfolio

**Preference:** Mix of growth and value

**Optimize for:**
```bash
python optimize_weights.py \
  --tickers AAPL MSFT GOOGL JPM V BAC JNJ PG \
  --date 2023-06-01 \
  --mode grid
```

**Likely result:** Balanced weights (0.40/0.50/0.10)

---

## Troubleshooting

### "No data available for ticker"
- Historical data insufficient
- Try a different start date (more recent)
- Some stocks may not have enough history

### "All backtests failed"
- Check internet connection
- Yahoo Finance may be rate-limiting
- Try fewer stocks or increase delays

### "Optimization taking too long"
- Reduce granularity (5 → 3)
- Use fewer tickers for testing
- Use 'grid' mode instead of 'composite'

### "Results seem random"
- Need more stocks for statistical significance
- Test on multiple time periods
- Check for data quality issues

---

## Next Steps

1. **Run baseline backtest** on your favorite stocks
2. **Analyze metric correlations** to see what's predictive
3. **Optimize weights** for your investment style
4. **Validate** on different time periods
5. **Update** `weights_config.json` with optimal weights
6. **Use** optimized weights for daily analysis

See also:
- [BATCH_ANALYZER_GUIDE.md](BATCH_ANALYZER_GUIDE.md) - Analyze 1000+ stocks
- [SCHEDULING_GUIDE.md](SCHEDULING_GUIDE.md) - Automate daily runs
- [README.md](../README.md) - Main documentation
