# Stock Analyzer 📊

A comprehensive Python-based stock analysis tool that combines **momentum analysis** and **fundamental analysis** to help investors identify promising opportunities.

## Features

### Momentum Analysis
- **Moving Averages**: 20-day, 50-day, 200-day SMA/EMA
- **RSI (Relative Strength Index)**: 14-period with overbought/oversold detection
- **MACD**: Signal line crossovers and histogram analysis
- **Volume Analysis**: Volume trends and price-volume correlation
- **Price Momentum**: Multi-period return analysis (1/3/6/12 months)
- **Trend Strength**: ADX (Average Directional Index)
- **Support/Resistance**: Key price level identification

### Fundamental Analysis
- **Valuation Metrics**: P/E, P/B, P/S, PEG, EV/EBITDA
- **Profitability**: Margins (gross, operating, net), ROE, ROA
- **Financial Health**: Debt-to-equity, liquidity ratios, cash flow
- **Growth Metrics**: Revenue and earnings growth, analyst targets

### Composite Scoring
- Combined 0-100 score with configurable weights (default: 40% momentum, 60% fundamental)
- Investment style classification
- Signal generation and risk warnings
- Clear buy/sell/hold recommendations

## Installation

1. **Clone the repository**
```bash
cd stock_analyzer
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Optional: Configure settings**
```bash
cp .env.example .env
# Edit .env to customize settings
```

## Usage

### Analyze a Single Stock
```bash
python main.py analyze AAPL
```

**Export to JSON:**
```bash
python main.py analyze AAPL --export aapl_analysis.json
```

### Compare Multiple Stocks
```bash
python main.py compare AAPL MSFT GOOGL
```

### Screen Stocks
```bash
python main.py screen AAPL MSFT GOOGL TSLA NVDA --momentum-min 70 --composite-min 65
```

**Advanced screening:**
```bash
python main.py screen AAPL MSFT GOOGL --momentum-min 70 --fundamental-min 60 --composite-min 70
```

### Monitor a Watchlist
```bash
python main.py watchlist AAPL MSFT NVDA META --alert-threshold 80
```

### Clear Cache
```bash
python main.py clear-cache
```

### Disable Caching
```bash
python main.py analyze AAPL --no-cache
```

## Scoring Methodology

### Momentum Score (0-100 points)
- **Moving Average Analysis** (0-20 points): Price position relative to 20/50/200-day MAs
- **RSI Analysis** (0-15 points): Relative strength with overbought/oversold detection
- **MACD Analysis** (0-15 points): Trend direction and momentum
- **Volume Analysis** (0-15 points): Volume trends and price-volume correlation
- **Price Momentum** (0-20 points): Multi-period return analysis
- **Trend Strength** (0-15 points): ADX-based trend strength measurement

### Fundamental Score (0-100 points)
- **Valuation Score** (0-25 points): P/E, PEG, P/B ratios vs benchmarks
- **Profitability Score** (0-25 points): Margins, ROE, earnings growth
- **Financial Health Score** (0-25 points): Debt levels, liquidity, cash flow
- **Growth Score** (0-25 points): Revenue/earnings growth, analyst upside

### Composite Score
```
Composite = (Momentum × 0.4) + (Fundamental × 0.6)
```

### Recommendation Thresholds
| Score Range | Recommendation |
|-------------|----------------|
| 80-100      | Strong Buy     |
| 65-79       | Buy            |
| 45-64       | Hold           |
| 30-44       | Sell           |
| 0-29        | Strong Avoid   |

## Configuration

Edit `.env` to customize settings:

```bash
# Scoring Weights (must sum to 1.0)
MOMENTUM_WEIGHT=0.4
FUNDAMENTAL_WEIGHT=0.6

# Cache Settings
CACHE_ENABLED=true
CACHE_EXPIRY_HOURS=24

# Technical Indicator Parameters
RSI_PERIOD=14
MACD_FAST=12
MACD_SLOW=26
MACD_SIGNAL=9

# Recommendation Thresholds
STRONG_BUY_THRESHOLD=80
BUY_THRESHOLD=65
HOLD_THRESHOLD=45
SELL_THRESHOLD=30
```

## Example Output

### Single Stock Analysis
```
╔══════════════════════════════════════════════════════════════╗
║ AAPL - Apple Inc.                                           ║
║ Sector: Technology | Industry: Consumer Electronics         ║
║ Current Price: $178.45                                      ║
╚══════════════════════════════════════════════════════════════╝

📊 Composite Analysis
┌─────────────────────┬────────────────────┐
│ Metric              │              Value │
├─────────────────────┼────────────────────┤
│ Composite Score     │              75.2/100 │
│ Recommendation      │              Buy    │
│                     │                    │
│ Momentum Score      │              72.0/100 │
│ Fundamental Score   │              77.3/100 │
│                     │                    │
│ Investment Style    │ Balanced/Moderate  │
│ Confidence          │ High (Strong Agreement) │
└─────────────────────┴────────────────────┘
```

## Sample Analysis Results

### Momentum Play Example: NVDA
- Momentum Score: **85/100** (Strong uptrend, positive MACD, high volume)
- Fundamental Score: **68/100** (High valuation, strong growth)
- Composite: **74.8/100** - **Buy** recommendation
- Style: Momentum/Growth Play

### Value Play Example: JNJ
- Momentum Score: **55/100** (Neutral trend, stable)
- Fundamental Score: **82/100** (Strong financials, reasonable valuation)
- Composite: **71.8/100** - **Buy** recommendation
- Style: Value/Quality Play

### Balanced Example: MSFT
- Momentum Score: **78/100** (Strong momentum indicators)
- Fundamental Score: **85/100** (Excellent fundamentals)
- Composite: **82.2/100** - **Strong Buy** recommendation
- Style: Strong Balanced Growth

## Data Sources

- **Market Data**: Yahoo Finance (via yfinance library)
- **Real-time quotes, historical prices, financial statements**
- **No API key required for basic functionality**

## Caching

The tool caches data locally to minimize API calls:
- Default cache location: `.cache/` directory
- Default expiry: 24 hours
- Cached data: Stock info, price history, financial statements

## Limitations

- Data accuracy depends on Yahoo Finance data quality
- Some metrics may not be available for all stocks (e.g., startups, foreign stocks)
- Historical performance does not guarantee future results
- This tool is for informational purposes only - not financial advice

## Project Structure

```
stock_analyzer/
├── main.py                 # CLI entry point
├── data/
│   ├── fetcher.py         # Data retrieval from yfinance
│   └── cache.py           # Local data caching system
├── analysis/
│   ├── momentum.py        # Technical indicators & momentum scoring
│   ├── fundamental.py     # Financial metrics & fundamental scoring
│   └── scoring.py         # Composite scoring system
├── utils/
│   ├── config.py          # Configuration management
│   └── output.py          # Rich terminal output formatting
├── requirements.txt       # Python dependencies
└── .env.example          # Configuration template
```

## Requirements

- Python 3.8+
- See `requirements.txt` for package dependencies

## Contributing

This is an educational project. Feel free to fork and customize for your needs.

## Disclaimer

⚠️ **This tool is for educational and informational purposes only. It does not constitute financial advice. Always do your own research and consult with a qualified financial advisor before making investment decisions.**

## License

MIT License - See LICENSE file for details

## Author

Built with Claude Code

## Version

1.0.0
