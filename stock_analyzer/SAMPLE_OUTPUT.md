# Sample Stock Analysis Output

This document shows example outputs from the Stock Analyzer tool.

## Single Stock Analysis Example

```bash
$ python main.py analyze AAPL
```

### Output:

```
╔══════════════════════════════════════════════════════════════╗
║ AAPL - Apple Inc.                                           ║
║ Sector: Technology | Industry: Consumer Electronics         ║
║ Current Price: $178.45                                      ║
╚══════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────┐
│                   📊 Composite Analysis                     │
├─────────────────────┬───────────────────────────────────────┤
│ Metric              │                            Value      │
├─────────────────────┼───────────────────────────────────────┤
│ Composite Score     │                          75.2/100    │
│ Recommendation      │                          Buy         │
│                     │                                       │
│ Momentum Score      │                          72.0/100    │
│ Fundamental Score   │                          77.3/100    │
│                     │                                       │
│ Investment Style    │                   Balanced/Moderate   │
│ Confidence          │            High (Strong Agreement)    │
└─────────────────────┴───────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              📈 Momentum Analysis Details                   │
├──────────────────────────────┬─────────────┬────────────────┤
│ Indicator                    │       Value │          Score │
├──────────────────────────────┼─────────────┼────────────────┤
│ RSI (14-period)             │       58.23 │          15/15 │
│ MACD                        │      Signal │          12/15 │
│ Moving Averages             │       Trend │          18/20 │
│ Volume Trend                │    Analysis │          11/15 │
│ Price Momentum              │ Multi-period│          16/20 │
│ Trend Strength (ADX)        │       32.5  │          10/15 │
└──────────────────────────────┴─────────────┴────────────────┘

Price Momentum Returns
┌──────────────┬────────────┐
│ Period       │     Return │
├──────────────┼────────────┤
│ 1 Month      │     +8.5%  │
│ 3 Month      │    +15.2%  │
│ 6 Month      │    +22.8%  │
│ 12 Month     │    +31.4%  │
└──────────────┴────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   💰 Valuation Metrics                      │
├─────────────────────────┬───────────────────────────────────┤
│ Metric                  │                           Value   │
├─────────────────────────┼───────────────────────────────────┤
│ P/E Ratio              │                            28.45   │
│ Forward P/E            │                            24.12   │
│ PEG Ratio              │                             2.15   │
│ P/B Ratio              │                            45.23   │
│ P/S Ratio              │                             7.35   │
│ EV/EBITDA              │                            21.54   │
│ Market Cap             │                        $2.85T     │
└─────────────────────────┴───────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                📊 Profitability Metrics                     │
├─────────────────────────┬───────────────────────────────────┤
│ Metric                  │                           Value   │
├─────────────────────────┼───────────────────────────────────┤
│ Gross Margin           │                           43.1%    │
│ Operating Margin       │                           30.2%    │
│ Net Margin             │                           25.3%    │
│ ROE                    │                          147.2%    │
│ ROA                    │                           28.5%    │
│ Earnings Growth        │                           11.2%    │
└─────────────────────────┴───────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    💪 Financial Health                      │
├─────────────────────────┬───────────────────────────────────┤
│ Metric                  │                           Value   │
├─────────────────────────┼───────────────────────────────────┤
│ Debt-to-Equity         │                             1.72   │
│ Current Ratio          │                             0.98   │
│ Quick Ratio            │                             0.83   │
│ Free Cash Flow         │                         $99.58B   │
│ Operating Cash Flow    │                        $110.54B   │
└─────────────────────────┴───────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    🚀 Growth Metrics                        │
├─────────────────────────┬───────────────────────────────────┤
│ Metric                  │                           Value   │
├─────────────────────────┼───────────────────────────────────┤
│ Revenue Growth         │                            8.2%    │
│ Earnings Growth        │                           11.2%    │
│ Analyst Upside         │                          +12.3%    │
│ Target Price           │                         $201.45    │
└─────────────────────────┴───────────────────────────────────┘

🎯 Signals & Alerts

Momentum Signals:
  • Price above major moving averages
  • Strong 12-month momentum (>30%)
  • RSI in healthy range

Fundamental Signals:
  • Attractive free cash flow generation
  • Strong profitability margins
  • Analyst upside potential: 12.3%

⚠️  Risk Warnings:
  • High P/B ratio: 45.23
  • Current ratio below 1.0 - liquidity watch
```

---

## Comparison Analysis Example

```bash
$ python main.py compare AAPL MSFT GOOGL
```

### Output:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          📊 Stock Comparison                                │
├──────────┬────────────┬────────────┬──────────────┬─────────────┬───────────┤
│ Ticker   │  Composite │   Momentum │  Fundamental │ Recommend.  │   Style   │
├──────────┼────────────┼────────────┼──────────────┼─────────────┼───────────┤
│ MSFT     │       82.2 │       78.0 │         85.0 │ Strong Buy  │ Strong    │
│          │            │            │              │             │ Balanced  │
│          │            │            │              │             │ Growth    │
├──────────┼────────────┼────────────┼──────────────┼─────────────┼───────────┤
│ AAPL     │       75.2 │       72.0 │         77.3 │ Buy         │ Balanced/ │
│          │            │            │              │             │ Moderate  │
├──────────┼────────────┼────────────┼──────────────┼─────────────┼───────────┤
│ GOOGL    │       71.8 │       68.5 │         74.0 │ Buy         │ Balanced/ │
│          │            │            │              │             │ Moderate  │
└──────────┴────────────┴────────────┴──────────────┴─────────────┴───────────┘
```

---

## Screening Example

```bash
$ python main.py screen AAPL MSFT GOOGL TSLA NVDA META --momentum-min 70 --composite-min 70
```

### Output:

```
Screening 6 stocks...
Criteria: Momentum >= 70, Fundamental >= 0, Composite >= 70

Found 4 stocks meeting criteria:

┌─────────────────────────────────────────────────────────────────────────────┐
│                          📊 Stock Comparison                                │
├──────────┬────────────┬────────────┬──────────────┬─────────────┬───────────┤
│ Ticker   │  Composite │   Momentum │  Fundamental │ Recommend.  │   Style   │
├──────────┼────────────┼────────────┼──────────────┼─────────────┼───────────┤
│ NVDA     │       84.5 │       88.0 │         82.0 │ Strong Buy  │ Momentum/ │
│          │            │            │              │             │ Growth    │
│          │            │            │              │             │ Play      │
├──────────┼────────────┼────────────┼──────────────┼─────────────┼───────────┤
│ MSFT     │       82.2 │       78.0 │         85.0 │ Strong Buy  │ Strong    │
│          │            │            │              │             │ Balanced  │
│          │            │            │              │             │ Growth    │
├──────────┼────────────┼────────────┼──────────────┼─────────────┼───────────┤
│ META     │       76.8 │       82.5 │         72.0 │ Buy         │ Momentum/ │
│          │            │            │              │             │ Growth    │
│          │            │            │              │             │ Play      │
├──────────┼────────────┼────────────┼──────────────┼─────────────┼───────────┤
│ AAPL     │       75.2 │       72.0 │         77.3 │ Buy         │ Balanced/ │
│          │            │            │              │             │ Moderate  │
└──────────┴────────────┴────────────┴──────────────┴─────────────┴───────────┘
```

---

## Investment Style Examples

### Momentum Play: NVDA
- **Momentum Score**: 88/100 (Exceptional momentum indicators)
- **Fundamental Score**: 82/100 (Strong growth, high valuations)
- **Composite**: 84.5/100 - **Strong Buy**
- **Style**: Momentum/Growth Play
- **Signals**: Strong uptrend, high RSI, exceptional price momentum

### Value Play: JNJ (Johnson & Johnson)
- **Momentum Score**: 55/100 (Neutral/stable trend)
- **Fundamental Score**: 82/100 (Excellent financials, reasonable valuation)
- **Composite**: 71.8/100 - **Buy**
- **Style**: Value/Quality Play
- **Signals**: Low debt, consistent dividends, stable profitability

### Balanced Growth: MSFT
- **Momentum Score**: 78/100 (Strong technical indicators)
- **Fundamental Score**: 85/100 (Excellent fundamentals across all metrics)
- **Composite**: 82.2/100 - **Strong Buy**
- **Style**: Strong Balanced Growth
- **Signals**: Best of both worlds - strong momentum AND fundamentals

---

## Notes

- All data shown is for illustrative purposes
- Actual output will vary based on current market conditions
- Scores are calculated using the methodology described in README.md
- Rich terminal formatting provides color-coded scores for easy interpretation
