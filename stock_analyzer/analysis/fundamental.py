"""Fundamental analysis using financial metrics."""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


class FundamentalAnalyzer:
    """Analyzes stock fundamentals using financial data."""

    def __init__(self, stock_info: Dict[str, Any], financials: Optional[Dict[str, pd.DataFrame]] = None):
        """Initialize fundamental analyzer.

        Args:
            stock_info: Dictionary with stock information from yfinance
            financials: Dictionary with financial statements (optional)
        """
        self.info = stock_info
        self.financials = financials

    def _safe_get(self, key: str, default: Any = None) -> Any:
        """Safely get value from stock info.

        Args:
            key: Key to retrieve
            default: Default value if key not found

        Returns:
            Value or default
        """
        return self.info.get(key, default)

    def get_valuation_metrics(self) -> Dict[str, Any]:
        """Calculate valuation metrics.

        Returns:
            Dictionary with valuation ratios
        """
        metrics = {}

        # P/E Ratio
        pe_ratio = self._safe_get('trailingPE')
        forward_pe = self._safe_get('forwardPE')
        metrics['pe_ratio'] = pe_ratio
        metrics['forward_pe'] = forward_pe

        # P/B Ratio
        pb_ratio = self._safe_get('priceToBook')
        metrics['pb_ratio'] = pb_ratio

        # P/S Ratio
        ps_ratio = self._safe_get('priceToSalesTrailing12Months')
        metrics['ps_ratio'] = ps_ratio

        # PEG Ratio
        peg_ratio = self._safe_get('pegRatio')
        metrics['peg_ratio'] = peg_ratio

        # EV/EBITDA
        ev_to_ebitda = self._safe_get('enterpriseToEbitda')
        metrics['ev_to_ebitda'] = ev_to_ebitda

        # Market Cap
        market_cap = self._safe_get('marketCap')
        metrics['market_cap'] = market_cap

        return metrics

    def get_profitability_metrics(self) -> Dict[str, Any]:
        """Calculate profitability metrics.

        Returns:
            Dictionary with profitability ratios
        """
        metrics = {}

        # Profit Margins
        metrics['gross_margin'] = self._safe_get('grossMargins')
        metrics['operating_margin'] = self._safe_get('operatingMargins')
        metrics['net_margin'] = self._safe_get('profitMargins')

        # Returns
        metrics['roe'] = self._safe_get('returnOnEquity')
        metrics['roa'] = self._safe_get('returnOnAssets')

        # Earnings
        metrics['earnings_growth'] = self._safe_get('earningsGrowth')
        metrics['earnings_quarterly_growth'] = self._safe_get('earningsQuarterlyGrowth')

        return metrics

    def get_financial_health_metrics(self) -> Dict[str, Any]:
        """Calculate financial health metrics.

        Returns:
            Dictionary with financial health indicators
        """
        metrics = {}

        # Debt Ratios
        debt_to_equity = self._safe_get('debtToEquity')
        metrics['debt_to_equity'] = debt_to_equity

        # Liquidity Ratios
        current_ratio = self._safe_get('currentRatio')
        quick_ratio = self._safe_get('quickRatio')
        metrics['current_ratio'] = current_ratio
        metrics['quick_ratio'] = quick_ratio

        # Cash Flow
        free_cash_flow = self._safe_get('freeCashflow')
        operating_cash_flow = self._safe_get('operatingCashflow')
        metrics['free_cash_flow'] = free_cash_flow
        metrics['operating_cash_flow'] = operating_cash_flow

        # Interest Coverage
        # Calculate from EBIT and interest expense if available
        ebitda = self._safe_get('ebitda')
        metrics['ebitda'] = ebitda

        return metrics

    def get_growth_metrics(self) -> Dict[str, Any]:
        """Calculate growth metrics.

        Returns:
            Dictionary with growth indicators
        """
        metrics = {}

        # Revenue Growth
        revenue_growth = self._safe_get('revenueGrowth')
        metrics['revenue_growth'] = revenue_growth

        # Earnings Growth
        earnings_growth = self._safe_get('earningsGrowth')
        earnings_quarterly_growth = self._safe_get('earningsQuarterlyGrowth')
        metrics['earnings_growth'] = earnings_growth
        metrics['earnings_quarterly_growth'] = earnings_quarterly_growth

        # Revenue and Earnings
        total_revenue = self._safe_get('totalRevenue')
        metrics['total_revenue'] = total_revenue

        # Target Prices
        target_high = self._safe_get('targetHighPrice')
        target_low = self._safe_get('targetLowPrice')
        target_mean = self._safe_get('targetMeanPrice')
        current_price = self._safe_get('currentPrice')

        metrics['target_high'] = target_high
        metrics['target_low'] = target_low
        metrics['target_mean'] = target_mean
        metrics['current_price'] = current_price

        if target_mean and current_price:
            metrics['upside_potential'] = ((target_mean - current_price) / current_price) * 100
        else:
            metrics['upside_potential'] = None

        return metrics

    def get_dividend_metrics(self) -> Dict[str, Any]:
        """Calculate dividend metrics.

        Returns:
            Dictionary with dividend information
        """
        metrics = {}

        dividend_yield = self._safe_get('dividendYield')
        dividend_rate = self._safe_get('dividendRate')
        payout_ratio = self._safe_get('payoutRatio')
        five_year_avg_yield = self._safe_get('fiveYearAvgDividendYield')

        metrics['dividend_yield'] = dividend_yield
        metrics['dividend_rate'] = dividend_rate
        metrics['payout_ratio'] = payout_ratio
        metrics['five_year_avg_yield'] = five_year_avg_yield

        return metrics

    def compare_to_sector(self) -> Dict[str, Any]:
        """Compare metrics to sector averages.

        Returns:
            Dictionary with sector comparison
        """
        sector = self._safe_get('sector', 'Unknown')
        industry = self._safe_get('industry', 'Unknown')

        return {
            'sector': sector,
            'industry': industry,
            'beta': self._safe_get('beta'),
            '52_week_high': self._safe_get('fiftyTwoWeekHigh'),
            '52_week_low': self._safe_get('fiftyTwoWeekLow'),
        }

    def get_fundamental_score(self) -> Dict[str, Any]:
        """Calculate comprehensive fundamental score (0-100).

        Returns:
            Dictionary with score and component analysis
        """
        scores = []
        components = {}

        # 1. Valuation Score (0-25 points)
        valuation = self.get_valuation_metrics()
        valuation_score = 0

        pe_ratio = valuation.get('pe_ratio')
        if pe_ratio:
            if 10 <= pe_ratio <= 20:
                valuation_score += 8
            elif 20 < pe_ratio <= 30:
                valuation_score += 5
            elif 5 <= pe_ratio < 10:
                valuation_score += 6

        peg_ratio = valuation.get('peg_ratio')
        if peg_ratio:
            if peg_ratio < 1:
                valuation_score += 9
            elif 1 <= peg_ratio <= 2:
                valuation_score += 5
            elif peg_ratio <= 3:
                valuation_score += 2

        pb_ratio = valuation.get('pb_ratio')
        if pb_ratio:
            if pb_ratio < 3:
                valuation_score += 8
            elif pb_ratio <= 5:
                valuation_score += 4

        scores.append(valuation_score)
        components['valuation_score'] = valuation_score
        components['valuation_metrics'] = valuation

        # 2. Profitability Score (0-25 points)
        profitability = self.get_profitability_metrics()
        profitability_score = 0

        roe = profitability.get('roe')
        if roe:
            if roe > 0.20:
                profitability_score += 10
            elif roe > 0.15:
                profitability_score += 7
            elif roe > 0.10:
                profitability_score += 4

        net_margin = profitability.get('net_margin')
        if net_margin:
            if net_margin > 0.20:
                profitability_score += 10
            elif net_margin > 0.10:
                profitability_score += 6
            elif net_margin > 0.05:
                profitability_score += 3

        earnings_growth = profitability.get('earnings_growth')
        if earnings_growth:
            if earnings_growth > 0.25:
                profitability_score += 5
            elif earnings_growth > 0.15:
                profitability_score += 3
            elif earnings_growth > 0:
                profitability_score += 1

        scores.append(profitability_score)
        components['profitability_score'] = profitability_score
        components['profitability_metrics'] = profitability

        # 3. Financial Health Score (0-25 points)
        health = self.get_financial_health_metrics()
        health_score = 0

        debt_to_equity = health.get('debt_to_equity')
        if debt_to_equity is not None:
            if debt_to_equity < 0.5:
                health_score += 10
            elif debt_to_equity < 1.0:
                health_score += 7
            elif debt_to_equity < 2.0:
                health_score += 3

        current_ratio = health.get('current_ratio')
        if current_ratio:
            if current_ratio > 2.0:
                health_score += 8
            elif current_ratio > 1.5:
                health_score += 6
            elif current_ratio > 1.0:
                health_score += 3

        free_cash_flow = health.get('free_cash_flow')
        if free_cash_flow and free_cash_flow > 0:
            health_score += 7

        scores.append(health_score)
        components['financial_health_score'] = health_score
        components['financial_health_metrics'] = health

        # 4. Growth Score (0-25 points)
        growth = self.get_growth_metrics()
        growth_score = 0

        revenue_growth = growth.get('revenue_growth')
        if revenue_growth:
            if revenue_growth > 0.20:
                growth_score += 10
            elif revenue_growth > 0.10:
                growth_score += 7
            elif revenue_growth > 0.05:
                growth_score += 4
            elif revenue_growth > 0:
                growth_score += 2

        earnings_growth = growth.get('earnings_growth')
        if earnings_growth:
            if earnings_growth > 0.25:
                growth_score += 10
            elif earnings_growth > 0.15:
                growth_score += 6
            elif earnings_growth > 0.05:
                growth_score += 3

        upside_potential = growth.get('upside_potential')
        if upside_potential:
            if upside_potential > 20:
                growth_score += 5
            elif upside_potential > 10:
                growth_score += 3
            elif upside_potential > 0:
                growth_score += 1

        scores.append(growth_score)
        components['growth_score'] = growth_score
        components['growth_metrics'] = growth

        # Calculate total score
        total_score = sum(scores)

        return {
            'score': total_score,
            'components': components,
            'sector_info': self.compare_to_sector(),
            'dividend_metrics': self.get_dividend_metrics()
        }
