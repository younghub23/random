"""Composite scoring system combining momentum and fundamental analysis."""
from typing import Dict, Any
from ..utils.config import Config


class CompositeScorer:
    """Combines momentum and fundamental scores into a composite score."""

    def __init__(self, momentum_analysis: Dict[str, Any], fundamental_analysis: Dict[str, Any]):
        """Initialize composite scorer.

        Args:
            momentum_analysis: Results from momentum analyzer
            fundamental_analysis: Results from fundamental analyzer
        """
        self.momentum = momentum_analysis
        self.fundamental = fundamental_analysis

    def calculate_composite_score(self) -> Dict[str, Any]:
        """Calculate weighted composite score.

        Returns:
            Dictionary with composite score and breakdown
        """
        momentum_score = self.momentum.get('score', 0)
        fundamental_score = self.fundamental.get('score', 0)

        # Apply weights from configuration
        composite_score = (
            momentum_score * Config.MOMENTUM_WEIGHT +
            fundamental_score * Config.FUNDAMENTAL_WEIGHT
        )

        # Get recommendation based on composite score
        recommendation = Config.get_recommendation(composite_score)

        # Determine investment style based on score breakdown
        investment_style = self._determine_investment_style(momentum_score, fundamental_score)

        # Generate signals
        signals = self._generate_signals()

        return {
            'composite_score': round(composite_score, 2),
            'momentum_score': round(momentum_score, 2),
            'fundamental_score': round(fundamental_score, 2),
            'recommendation': recommendation,
            'investment_style': investment_style,
            'signals': signals,
            'confidence': self._calculate_confidence(momentum_score, fundamental_score)
        }

    def _determine_investment_style(self, momentum_score: float, fundamental_score: float) -> str:
        """Determine the investment style based on score breakdown.

        Args:
            momentum_score: Momentum analysis score
            fundamental_score: Fundamental analysis score

        Returns:
            Investment style description
        """
        # High momentum, high fundamental = Balanced Growth
        if momentum_score >= 70 and fundamental_score >= 70:
            return "Strong Balanced Growth"

        # High momentum, lower fundamental = Momentum Play
        elif momentum_score >= 70 and fundamental_score < 70:
            return "Momentum/Growth Play"

        # Lower momentum, high fundamental = Value Play
        elif momentum_score < 70 and fundamental_score >= 70:
            return "Value/Quality Play"

        # Both moderate = Balanced
        elif 50 <= momentum_score < 70 and 50 <= fundamental_score < 70:
            return "Balanced/Moderate"

        # Both low = Avoid
        else:
            return "Weak Fundamentals & Momentum"

    def _generate_signals(self) -> Dict[str, Any]:
        """Generate buy/sell/hold signals based on analysis.

        Returns:
            Dictionary with various signals
        """
        signals = {
            'momentum_signals': [],
            'fundamental_signals': [],
            'risk_warnings': []
        }

        # Momentum signals
        momentum_components = self.momentum.get('components', {})

        # RSI signals
        rsi_value = momentum_components.get('rsi_value')
        if rsi_value:
            if rsi_value > 70:
                signals['momentum_signals'].append(f"RSI overbought at {rsi_value:.1f}")
                signals['risk_warnings'].append("Potentially overbought - short-term pullback risk")
            elif rsi_value < 30:
                signals['momentum_signals'].append(f"RSI oversold at {rsi_value:.1f}")
                signals['momentum_signals'].append("Potential bounce opportunity")

        # Price momentum
        price_momentum = momentum_components.get('price_momentum', {})
        if price_momentum.get('12_month', 0) > 50:
            signals['momentum_signals'].append("Strong 12-month momentum (>50%)")
        elif price_momentum.get('12_month', 0) < -20:
            signals['momentum_signals'].append("Weak 12-month momentum (<-20%)")

        # Moving average signals
        if momentum_components.get('moving_average_score', 0) >= 15:
            signals['momentum_signals'].append("Price above major moving averages")

        # Fundamental signals
        fundamental_components = self.fundamental.get('components', {})

        # Valuation
        valuation_metrics = fundamental_components.get('valuation_metrics', {})
        peg_ratio = valuation_metrics.get('peg_ratio')
        if peg_ratio and peg_ratio < 1:
            signals['fundamental_signals'].append(f"Attractive PEG ratio: {peg_ratio:.2f}")
        elif peg_ratio and peg_ratio > 3:
            signals['risk_warnings'].append(f"High PEG ratio: {peg_ratio:.2f}")

        # Growth
        growth_metrics = fundamental_components.get('growth_metrics', {})
        upside = growth_metrics.get('upside_potential')
        if upside and upside > 20:
            signals['fundamental_signals'].append(f"Analyst upside potential: {upside:.1f}%")
        elif upside and upside < -10:
            signals['risk_warnings'].append(f"Analyst downside risk: {upside:.1f}%")

        # Financial health
        health_metrics = fundamental_components.get('financial_health_metrics', {})
        debt_to_equity = health_metrics.get('debt_to_equity')
        if debt_to_equity and debt_to_equity > 2:
            signals['risk_warnings'].append(f"High debt-to-equity: {debt_to_equity:.2f}")

        return signals

    def _calculate_confidence(self, momentum_score: float, fundamental_score: float) -> str:
        """Calculate confidence level in the recommendation.

        Args:
            momentum_score: Momentum analysis score
            fundamental_score: Fundamental analysis score

        Returns:
            Confidence level (High/Medium/Low)
        """
        # High confidence if both scores agree (both high or both low)
        score_diff = abs(momentum_score - fundamental_score)

        if score_diff < 15:
            if momentum_score >= 70 and fundamental_score >= 70:
                return "High (Strong Agreement)"
            elif momentum_score <= 40 and fundamental_score <= 40:
                return "High (Both Weak)"
            else:
                return "Medium"
        elif score_diff < 30:
            return "Medium (Moderate Divergence)"
        else:
            return "Low (Significant Divergence)"

    def get_detailed_report(self) -> Dict[str, Any]:
        """Generate a comprehensive analysis report.

        Returns:
            Dictionary with complete analysis
        """
        composite = self.calculate_composite_score()

        return {
            'composite_analysis': composite,
            'momentum_details': self.momentum,
            'fundamental_details': self.fundamental
        }

    def compare_stocks(self, other_scorer: 'CompositeScorer') -> Dict[str, Any]:
        """Compare this stock with another.

        Args:
            other_scorer: Another CompositeScorer instance

        Returns:
            Comparison results
        """
        this_composite = self.calculate_composite_score()
        other_composite = other_scorer.calculate_composite_score()

        return {
            'this_score': this_composite['composite_score'],
            'other_score': other_composite['composite_score'],
            'score_difference': this_composite['composite_score'] - other_composite['composite_score'],
            'this_recommendation': this_composite['recommendation'],
            'other_recommendation': other_composite['recommendation'],
            'better_momentum': 'This' if this_composite['momentum_score'] > other_composite['momentum_score'] else 'Other',
            'better_fundamental': 'This' if this_composite['fundamental_score'] > other_composite['fundamental_score'] else 'Other'
        }
