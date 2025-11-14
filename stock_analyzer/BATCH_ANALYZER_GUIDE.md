# Batch Stock Analyzer Guide

The batch analyzer allows you to analyze large universes of stocks (up to 1000+) and automatically identify the best investment opportunities.

## Quick Start

### Analyze S&P 500 stocks:
```bash
python batch_analyzer.py
```

### Analyze top 100 stocks from S&P 500:
```bash
python batch_analyzer.py --max-stocks 100
```

### Analyze NASDAQ 100:
```bash
python batch_analyzer.py --universe nasdaq100
```

### Analyze Russell 1000 (extended universe):
```bash
python batch_analyzer.py --universe sp1000
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--universe` | Stock universe to analyze (`sp500`, `sp1000`, `nasdaq100`, `custom`) | `sp500` |
| `--max-stocks` | Maximum number of stocks to analyze | All in universe |
| `--delay` | Delay between API calls in seconds (for rate limiting) | `0.5` |
| `--min-score` | Minimum composite score threshold | `0` |
| `--no-cache` | Disable caching (fetch fresh data) | Cache enabled |
| `--output` | Output filename (without extension) | Auto-generated timestamp |

## Examples

### Find top 50 stocks from S&P 500:
```bash
python batch_analyzer.py --max-stocks 50 --output sp500_top50
```

### Analyze tech-heavy NASDAQ 100 with fresh data:
```bash
python batch_analyzer.py --universe nasdaq100 --no-cache
```

### Screen for high-quality stocks (score >= 70):
```bash
python batch_analyzer.py --max-stocks 200 --min-score 70
```

### Fast analysis with minimal delays (use with caution):
```bash
python batch_analyzer.py --max-stocks 100 --delay 0.2
```

## Output

The batch analyzer produces:

### 1. Terminal Summary
- **Overall Statistics**: Average scores across all analyzed stocks
- **Recommendation Breakdown**: Distribution of Buy/Sell/Hold recommendations
- **Top 20 Stocks**: Highest composite scores
- **Best by Sector**: Top 3 stocks in each sector
- **Investment Opportunities**: Categorized lists (Strong Buys, Momentum Plays, Value Plays, etc.)

### 2. Saved Files
Three files are automatically saved:

**`stock_analysis_TIMESTAMP.json`** - Full analysis results with all data
**`stock_analysis_TIMESTAMP.csv`** - Summary spreadsheet for Excel/Google Sheets
**`stock_analysis_TIMESTAMP_top50.csv`** - Top 50 stocks only

## Understanding Results

### Top Stock Categories

**🏆 Top 20 Stocks**
- Ranked by composite score (momentum + fundamentals)
- Best overall opportunities across all criteria

**🎯 Best by Sector**
- Top 3 stocks in each sector (Technology, Healthcare, Financials, etc.)
- Ensures sector diversification

**💡 Investment Opportunities**

1. **Strong Buys** - Composite score >= 80
2. **Momentum Plays** - Momentum score >= 75 (trending up)
3. **Value Plays** - Fundamental score >= 75 (undervalued with strong financials)
4. **Balanced Growth** - Both momentum AND fundamental >= 70
5. **High Conviction** - Scores agree strongly (low divergence)

## Sample Workflow

### Find best stocks for a diversified portfolio:

```bash
# 1. Analyze S&P 500
python batch_analyzer.py --max-stocks 500 --output analysis_2024

# 2. Review terminal output for top stocks

# 3. Open analysis_2024_top50.csv in Excel/Sheets

# 4. Filter by sector to ensure diversification

# 5. Review individual stocks with detailed analysis:
python main.py analyze AAPL
python main.py analyze MSFT
python main.py analyze GOOGL
```

### Weekly screening routine:

```bash
# Monday: Screen entire S&P 500 for new opportunities
python batch_analyzer.py --no-cache --output weekly_screen

# Review results and create watchlist of top 20 stocks

# Daily: Monitor watchlist
python main.py watchlist AAPL MSFT NVDA GOOGL --alert-threshold 75
```

## Performance Tips

### Speed vs. Rate Limits
- **Default delay (0.5s)**: ~7 stocks/minute, safe for extended runs
- **Faster (0.2s)**: ~15 stocks/minute, may hit rate limits
- **Slower (1.0s)**: ~3 stocks/minute, very conservative

### Caching Strategy
- **First run**: Use default cache to speed up subsequent analyses
- **Weekly updates**: Use `--no-cache` to get fresh data
- **Quick re-analysis**: Keep cache enabled

### Managing Large Runs
```bash
# For 500+ stocks, run overnight or in stages:

# Stage 1: First 200 stocks
python batch_analyzer.py --max-stocks 200 --output batch1

# Stage 2: Next 200 stocks (requires manual ticker list modification)
# Or run smaller focused analyses:

python batch_analyzer.py --universe nasdaq100 --output tech_focus
python batch_analyzer.py --universe sp500 --max-stocks 100 --min-score 70
```

## Stock Universes

### S&P 500 (`sp500`)
- ~500 large-cap US stocks
- Broad sector diversification
- Most liquid and well-known companies
- **Best for**: General portfolio building

### Russell 1000 / Extended (`sp1000`)
- ~1000 large and mid-cap stocks
- Includes S&P 500 + growth mid-caps
- More opportunities in emerging leaders
- **Best for**: Finding growth stocks

### NASDAQ 100 (`nasdaq100`)
- ~100 largest NASDAQ stocks
- Tech-heavy (60%+ technology)
- High growth potential, higher risk
- **Best for**: Tech-focused portfolios

## Interpreting Scores

### Composite Score Ranges:
- **80-100**: Strong Buy - Excellent opportunity
- **65-79**: Buy - Good opportunity
- **45-64**: Hold - Neutral
- **30-44**: Sell - Weak
- **0-29**: Strong Avoid - Poor fundamentals and momentum

### Investment Style Meanings:

**"Strong Balanced Growth"**
- High momentum (70+) AND high fundamentals (70+)
- Best overall stocks - rare finds
- Low risk, high conviction

**"Momentum/Growth Play"**
- High momentum, moderate fundamentals
- Riding the trend
- Higher risk, time-sensitive

**"Value/Quality Play"**
- High fundamentals, moderate momentum
- Undervalued with strong business
- Lower risk, patience required

**"Balanced/Moderate"**
- Both scores 50-70
- Steady stocks
- Medium risk and reward

## Troubleshooting

### "403 Error from Yahoo Finance"
- Yahoo is rate-limiting your IP
- Increase `--delay` to 1.0 or higher
- Wait 10-15 minutes and try again
- Use `--max-stocks` to analyze fewer stocks at once

### "No results to summarize"
- All stocks failed to fetch data
- Check internet connection
- Try with a smaller universe first
- Verify ticker symbols are valid

### Slow performance
- Expected! Analyzing 500 stocks takes ~45-60 minutes
- Use `--max-stocks` to limit scope
- Run overnight for large batches
- Enable caching for subsequent runs

## Advanced Usage

### Custom Stock Universe

Edit `batch_analyzer.py` and modify `_get_custom_universe()` to analyze your own list:

```python
def _get_custom_universe(self) -> List[str]:
    """Your custom stock list."""
    return [
        'AAPL', 'MSFT', 'GOOGL',  # Your picks
        # Add more tickers...
    ]
```

Then run:
```bash
python batch_analyzer.py --universe custom
```

### Export for Further Analysis

The CSV files can be imported into:
- Excel/Google Sheets for filtering and charting
- Python pandas for custom analysis
- Portfolio management tools
- Your own trading systems

## Example Output

```
📋 Selected SP500 universe: 503 stocks

🔍 Analyzing 503 stocks...

[1/503] Analyzing AAPL... ✓ Score: 75.2 (Buy)
[2/503] Analyzing MSFT... ✓ Score: 82.1 (Strong Buy)
[3/503] Analyzing GOOGL... ✓ Score: 71.8 (Buy)
...

✅ Successfully analyzed 487 out of 503 stocks

================================================================================
📊 BATCH ANALYSIS SUMMARY
================================================================================

Total Stocks Analyzed: 487
Average Composite Score: 58.34
Average Momentum Score: 54.21
Average Fundamental Score: 61.15

Recommendations Breakdown:
  Hold: 243 (49.9%)
  Buy: 156 (32.0%)
  Strong Buy: 48 (9.9%)
  Sell: 32 (6.6%)
  Strong Avoid: 8 (1.6%)

================================================================================
🏆 TOP 20 STOCKS
================================================================================
[Formatted table with top performers]

================================================================================
🎯 BEST STOCKS BY SECTOR
================================================================================
[Grouped by sector with top 3 in each]

================================================================================
💡 INVESTMENT OPPORTUNITIES
================================================================================
[Categorized lists of opportunities]

✓ Saved full results to stock_analysis_20240115_143022.json
✓ Saved summary to stock_analysis_20240115_143022.csv
✓ Saved top 50 stocks to stock_analysis_20240115_143022_top50.csv

✅ Analysis complete!
```

## Best Practices

1. **Start small**: Test with `--max-stocks 20` first
2. **Use caching**: Don't use `--no-cache` unless necessary
3. **Be patient**: Large batches take time (1-2 hours for 500+ stocks)
4. **Review sectors**: Don't just pick top scores - diversify across sectors
5. **Cross-check**: Use regular `main.py analyze` for detailed review of top picks
6. **Schedule regular runs**: Weekly or monthly batch analysis to catch new opportunities
7. **Respect rate limits**: Increase delays if you get errors

## Questions?

See the main README.md for general usage or run:
```bash
python batch_analyzer.py -h
```
