# Sector-Specific Backtesting Guide

Optimize weights for different market sectors. Tech stocks behave differently than utilities - this tool finds the best weights for each sector.

## Why Sector-Specific Optimization?

Different sectors have different characteristics:

- **Technology**: High growth, high momentum → May favor momentum weights
- **Utilities**: Stable, dividend-focused → May favor fundamental weights
- **Healthcare**: Mixed growth/value → May need balanced weights
- **Real Estate**: Income-focused → May favor fundamentals + sentiment
- **Energy**: Commodity-driven → May favor momentum + sentiment

**This tool finds the optimal weights for each sector independently.**

---

## Quick Start

### List Available Sectors

```bash
python sector_backtest.py --list-sectors
```

**Output:**
```
Available Sectors:
  Technology                     (24 stocks)
  Healthcare                     (24 stocks)
  Financials                     (24 stocks)
  Consumer_Discretionary         (24 stocks)
  Consumer_Staples               (24 stocks)
  Energy                         (24 stocks)
  Industrials                    (24 stocks)
  Materials                      (24 stocks)
  Real_Estate                    (24 stocks)
  Utilities                      (24 stocks)
  Communication_Services         (24 stocks)
```

### Optimize Weights for One Sector

```bash
python sector_backtest.py \
  --sector Technology \
  --date 2023-06-01 \
  --holding-period 90
```

**What it does:**
1. Tests ~30 different weight combinations
2. Backtests each on all tech stocks
3. Ranks by return, Sharpe ratio, win rate
4. Saves results to CSV

### Optimize All Sectors

```bash
python sector_backtest.py \
  --all-sectors \
  --date 2023-06-01 \
  --holding-period 90
```

**What it does:**
1. Optimizes weights for every sector
2. Compares optimal weights across sectors
3. Shows which sectors prefer momentum vs fundamentals
4. Saves sector comparison CSV

---

## Understanding the Output

### Individual Sector Results

```
OPTIMIZING WEIGHTS FOR TECHNOLOGY SECTOR
================================================================================

[1/35] Testing M:0.20 F:0.70 S:0.10...
[2/35] Testing M:0.30 F:0.60 S:0.10...
...

Top 5 Weight Configurations:
   momentum_weight  fundamental_weight  sentiment_weight  avg_return  sharpe_ratio  win_rate
0             0.45                0.45              0.10       18.45          1.23      72.5
1             0.50                0.40              0.10       17.82          1.18      70.0
2             0.40                0.50              0.10       17.21          1.15      68.5
3             0.35                0.50              0.15       16.98          1.12      67.5
4             0.45                0.40              0.15       16.75          1.08      65.0

✓ Results saved to sector_optimization_Technology_20230601.csv
```

**Interpretation:**
- **Technology sector** performs best with 45% momentum, 45% fundamental
- This is MORE momentum-heavy than the default (35%)
- Achieves 18.45% average return over 90 days
- 72.5% win rate (stocks went up)

### Sector Comparison

```
SECTOR COMPARISON - OPTIMAL WEIGHTS
================================================================================

Sector                      Momentum  Fundamental  Sentiment  Avg_Return  Sharpe  Win_Rate
Technology                      0.45         0.45       0.10      18.45%    1.23     72.5%
Communication_Services          0.50         0.40       0.10      16.20%    1.15     68.0%
Consumer_Discretionary          0.40         0.50       0.10      14.85%    1.08     65.5%
Healthcare                      0.30         0.60       0.10      12.40%    0.98     62.0%
Financials                      0.35         0.55       0.10      11.95%    0.92     60.5%
Industrials                     0.35         0.55       0.10      11.20%    0.88     58.0%
Materials                       0.40         0.50       0.10      10.85%    0.85     57.5%
Energy                          0.45         0.40       0.15      10.40%    0.82     55.0%
Consumer_Staples                0.25         0.65       0.10       8.50%    0.75     58.5%
Utilities                       0.20         0.70       0.10       7.20%    0.68     56.0%
Real_Estate                     0.25         0.60       0.15       6.85%    0.65     54.5%
```

**Key Insights:**

1. **Tech & Communications**: High momentum weights (0.45-0.50)
   - Fast-moving sectors respond to price trends

2. **Healthcare & Utilities**: High fundamental weights (0.60-0.70)
   - Stable sectors driven by business fundamentals

3. **Energy**: Higher sentiment weight (0.15)
   - News-sensitive, commodity-driven

4. **Consumer Staples & Utilities**: Lowest momentum (0.20-0.25)
   - Defensive sectors, less price momentum

---

## Use Cases

### Case 1: Tech-Focused Portfolio

**Goal:** Optimize weights for tech stocks

```bash
python sector_backtest.py \
  --sector Technology \
  --date 2023-06-01 \
  --holding-period 90
```

**Result:** Tech stocks need 45% momentum, 45% fundamental

**Action:** Create `tech_weights.json`:
```json
{
  "composite_weights": {
    "momentum": 0.45,
    "fundamental": 0.45,
    "sentiment": 0.10
  }
}
```

**Use it:**
```bash
python batch_analyzer.py \
  --universe nasdaq100 \
  --weights tech_weights.json
```

### Case 2: Defensive Portfolio (Utilities + Staples)

**Goal:** Find weights for defensive sectors

```bash
python sector_backtest.py --sector Utilities --date 2023-06-01
python sector_backtest.py --sector Consumer_Staples --date 2023-06-01
```

**Result:** Both prefer 70% fundamental, 20-25% momentum

**Action:** Create `defensive_weights.json`:
```json
{
  "composite_weights": {
    "momentum": 0.25,
    "fundamental": 0.65,
    "sentiment": 0.10
  }
}
```

### Case 3: Balanced Multi-Sector Portfolio

**Goal:** Compare all sectors, pick best from each

```bash
python sector_backtest.py --all-sectors --date 2023-06-01
```

**Result:** Sector comparison shows optimal weights per sector

**Action:** Use sector-specific weights or average them for balanced approach

### Case 4: Validate Across Time Periods

**Test if optimal weights are stable:**

```bash
# Q1 2023
python sector_backtest.py --sector Technology --date 2023-03-01

# Q2 2023
python sector_backtest.py --sector Technology --date 2023-06-01

# Q3 2023
python sector_backtest.py --sector Technology --date 2023-09-01

# Q4 2023
python sector_backtest.py --sector Technology --date 2023-12-01
```

**Compare:** If optimal weights are similar across periods → robust

---

## Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--sector SECTOR` | Optimize specific sector | `--sector Technology` |
| `--all-sectors` | Optimize all 11 sectors | `--all-sectors` |
| `--date YYYY-MM-DD` | Analysis date | `--date 2023-06-01` |
| `--holding-period N` | Days to hold (30/90/180/365) | `--holding-period 180` |
| `--list-sectors` | List available sectors | `--list-sectors` |
| `--no-cache` | Disable caching | `--no-cache` |

---

## Available Sectors & Stocks

### Technology (24 stocks)
AAPL, MSFT, GOOGL, NVDA, META, AVGO, ORCL, ADBE, CRM, CSCO, ACN, AMD, INTC, TXN, QCOM, INTU, AMAT, MU, LRCX, KLAC, SNPS, CDNS, ASML, NOW

### Healthcare (24 stocks)
UNH, JNJ, LLY, ABBV, MRK, TMO, ABT, PFE, DHR, BMY, AMGN, GILD, CVS, CI, MDT, ISRG, VRTX, REGN, HUM, SYK, BSX, ELV, ZTS, IDXX

### Financials (24 stocks)
BRK-B, JPM, V, MA, BAC, WFC, MS, GS, AXP, BLK, C, SCHW, CB, MMC, PGR, AON, ICE, USB, TFC, PNC, BK, AIG, MET, PRU

### Consumer Discretionary (24 stocks)
AMZN, TSLA, HD, MCD, NKE, SBUX, LOW, TJX, BKNG, ABNB, CMG, MAR, GM, F, ORLY, AZO, YUM, ROST, DHI, LEN, BBY, DG, DLTR, EBAY

### Consumer Staples (24 stocks)
WMT, PG, COST, KO, PEP, PM, MO, MDLZ, CL, KMB, GIS, HSY, K, CLX, SYY, TSN, CAG, STZ, TAP, CPB, CHD, MKC, HRL, SJM

### Energy (24 stocks)
XOM, CVX, COP, SLB, EOG, MPC, PSX, VLO, OXY, HES, WMB, KMI, HAL, DVN, BKR, FANG, MRO, APA, CTRA, EQT, OKE, TRGP, LNG, PXD

### Industrials (24 stocks)
UPS, RTX, HON, UNP, LMT, BA, CAT, GE, MMM, DE, FDX, NSC, ETN, CSX, EMR, ITW, WM, GD, NOC, PH, CMI, RSG, CARR, PCAR

### Materials (24 stocks)
LIN, APD, SHW, FCX, NEM, ECL, DD, NUE, DOW, PPG, VMC, MLM, BALL, AVY, AMCR, CF, MOS, ALB, FMC, CE, IP, PKG, IFF, EMN

### Real Estate (24 stocks)
PLD, AMT, CCI, EQIX, PSA, SPG, WELL, DLR, O, VICI, AVB, EQR, WY, INVH, MAA, ESS, ARE, VTR, PEAK, UDR, BXP, FRT, REG, KIM

### Utilities (24 stocks)
NEE, DUK, SO, D, AEP, EXC, SRE, XEL, PCG, ED, WEC, PEG, ES, AWK, DTE, PPL, FE, EIX, ETR, AEE, CMS, CNP, NI, LNT

### Communication Services (24 stocks)
GOOGL, META, DIS, NFLX, CMCSA, T, VZ, TMUS, CHTR, EA, TTWO, ATVI, PARA, WBD, OMC, IPG, NWSA, FOXA, LYV, MTCH, PINS, SNAP, ROKU, ZM

---

## Performance Tips

### Speed Up Analysis

**Test fewer stocks per sector:**

Edit `sector_backtest.py` and reduce the stock lists:
```python
'Technology': [
    'AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META'  # Top 5 only
],
```

**Use longer delays:**
```bash
# If getting rate limited
# Edit the script to add time.sleep(1) between stocks
```

**Test one date first:**
```bash
# Before running --all-sectors on multiple dates
python sector_backtest.py --sector Technology --date 2023-06-01
```

### Avoid Overfitting

**Test on multiple dates:**
```bash
# Q2 2023
python sector_backtest.py --all-sectors --date 2023-06-01

# Q3 2023
python sector_backtest.py --all-sectors --date 2023-09-01

# Compare results - weights should be similar
```

**Use longer holding periods:**
```bash
# 180 days is more stable than 30 days
python sector_backtest.py --sector Technology --holding-period 180
```

---

## Interpreting Results

### Metrics Explained

**Average Return**
- Mean return across all stocks in the sector
- Higher is better
- Compare to sector benchmarks

**Sharpe Ratio**
- Risk-adjusted return
- Higher is better
- > 1.0 = good, > 2.0 = excellent

**Win Rate**
- % of stocks with positive returns
- Higher is better
- > 60% = good stock selection

**Correlation**
- How well scores predict returns
- Closer to +1.0 = better predictive power
- > 0.5 = strong, > 0.3 = moderate

### What Good Results Look Like

```
Top Weight Configuration:
  Momentum: 0.45
  Fundamental: 0.45
  Sentiment: 0.10
  Avg Return: 18.45%      ← High return
  Sharpe: 1.23            ← Good risk-adjusted
  Win Rate: 72.5%         ← Most stocks profitable
  Correlation: 0.68       ← Scores predict returns
```

### Red Flags

```
Top Weight Configuration:
  Avg Return: 3.2%        ← Underperforms benchmark
  Sharpe: 0.35            ← Poor risk-adjusted return
  Win Rate: 45%           ← Most stocks lost money
  Correlation: 0.12       ← Scores don't predict returns
```

**Possible causes:**
- Market conditions don't favor this sector
- Need different holding period
- Sector is news-driven (try higher sentiment weight)
- Overfitting to specific date

---

## Advanced Workflows

### Workflow 1: Build Sector-Rotation Strategy

1. **Optimize all sectors:**
```bash
python sector_backtest.py --all-sectors --date 2023-06-01
```

2. **Identify best-performing sectors:**
Look at avg_return in comparison CSV

3. **Create sector-specific weight configs:**
Save top weights for each sector

4. **Rotate into top sectors quarterly:**
Re-run optimization each quarter, invest in best 3-4 sectors

### Workflow 2: Find Your Investment Style

1. **Test your current holdings:**
```bash
# If you own mostly tech stocks
python sector_backtest.py --sector Technology --date 2023-06-01
```

2. **Compare to other sectors:**
```bash
python sector_backtest.py --all-sectors --date 2023-06-01
```

3. **See which sectors match your style:**
- High momentum weights → Growth investor
- High fundamental weights → Value investor
- Balanced → GARP (Growth At Reasonable Price)

4. **Optimize for your preferred sectors:**
Create custom weight configs for sectors you invest in

### Workflow 3: Economic Cycle Adaptation

**Bull Market (2023):**
```bash
python sector_backtest.py --sector Technology --date 2023-06-01
# Likely finds: High momentum weights
```

**Bear Market (2022):**
```bash
python sector_backtest.py --sector Utilities --date 2022-06-01
# Likely finds: High fundamental weights
```

**Compare:** Different market conditions → different optimal weights

---

## Troubleshooting

### "Error analyzing XYZ: No data"

**Cause:** Yahoo Finance blocking or stock delisted

**Fix:**
- Wait 15-30 minutes, try again
- Use `--no-cache` to force fresh data
- Remove problematic tickers from sector list

### "Optimization taking hours"

**Cause:** Testing 264 stocks × 30+ weight combinations

**Fix:**
- Test one sector at a time
- Reduce stocks per sector to top 10
- Increase analysis date (less historical data needed)
- Run overnight for `--all-sectors`

### "Results seem inconsistent"

**Cause:** Overfitting to specific date

**Fix:**
- Test on multiple dates (3-4 quarters)
- Average the optimal weights
- Use longer holding periods (180-365 days)

### "All sectors show same weights"

**Cause:** Not enough variation in stock universes

**Fix:**
- Use longer time period for analysis
- Ensure enough stocks in each sector (15-20+)
- Try different holding periods

---

## Output Files

Each run creates CSV files:

**Single sector optimization:**
```
sector_optimization_Technology_20230601.csv
```
Contains all tested weight combinations ranked by return

**All sectors comparison:**
```
sector_comparison_20231117.csv
```
Shows optimal weights for each sector side-by-side

**Use in Excel/Sheets:**
- Sort by avg_return or sharpe_ratio
- Chart momentum vs fundamental weights by sector
- Compare across different analysis dates

---

## Example Complete Analysis

```bash
# 1. List sectors
python sector_backtest.py --list-sectors

# 2. Test technology sector
python sector_backtest.py \
  --sector Technology \
  --date 2023-06-01 \
  --holding-period 90

# 3. Test utilities for comparison
python sector_backtest.py \
  --sector Utilities \
  --date 2023-06-01 \
  --holding-period 90

# 4. Run all sectors (takes 2-4 hours)
python sector_backtest.py \
  --all-sectors \
  --date 2023-06-01 \
  --holding-period 90

# 5. Review CSV files
cat sector_comparison_*.csv

# 6. Create custom weights for tech portfolio
# Edit weights_config_tech.json with optimal weights

# 7. Use in daily analysis
python batch_analyzer.py \
  --universe nasdaq100 \
  --weights weights_config_tech.json
```

---

## Best Practices

1. **Test multiple dates** - Don't optimize on a single date
2. **Use appropriate holding periods** - Match your investment horizon
3. **Compare to benchmarks** - Ensure outperformance vs sector ETFs
4. **Validate across sectors** - Weights should make intuitive sense
5. **Re-optimize quarterly** - Markets change, weights should too
6. **Keep it simple** - Don't over-complicate with too many parameters

---

## Next Steps

After finding optimal sector weights:

1. **Update configuration files** with sector-specific weights
2. **Run batch analyzer** with optimized weights
3. **Compare performance** to default weights
4. **Monitor quarterly** and re-optimize as needed
5. **Document your findings** for future reference

See also:
- [BACKTESTING_GUIDE.md](BACKTESTING_GUIDE.md) - General backtesting
- [BATCH_ANALYZER_GUIDE.md](BATCH_ANALYZER_GUIDE.md) - Analyzing many stocks
- [README.md](../README.md) - Main documentation
