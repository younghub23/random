"""Output formatting utilities for displaying analysis results."""
from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
import json


class OutputFormatter:
    """Formats and displays analysis results."""

    def __init__(self):
        """Initialize the output formatter."""
        self.console = Console()

    def _get_score_color(self, score: float) -> str:
        """Get color based on score value.

        Args:
            score: Score value (0-100)

        Returns:
            Color name for rich
        """
        if score >= 80:
            return "green"
        elif score >= 65:
            return "cyan"
        elif score >= 45:
            return "yellow"
        elif score >= 30:
            return "orange1"
        else:
            return "red"

    def _format_number(self, value: Any, prefix: str = "", suffix: str = "", decimals: int = 2) -> str:
        """Format a number for display.

        Args:
            value: Number to format
            prefix: Prefix string (e.g., '$')
            suffix: Suffix string (e.g., '%')
            decimals: Number of decimal places

        Returns:
            Formatted string
        """
        if value is None:
            return "N/A"

        if isinstance(value, (int, float)):
            if abs(value) >= 1e12:
                return f"{prefix}{value/1e12:.{decimals}f}T{suffix}"
            elif abs(value) >= 1e9:
                return f"{prefix}{value/1e9:.{decimals}f}B{suffix}"
            elif abs(value) >= 1e6:
                return f"{prefix}{value/1e6:.{decimals}f}M{suffix}"
            else:
                return f"{prefix}{value:.{decimals}f}{suffix}"

        return str(value)

    def print_stock_header(self, ticker: str, info: Dict[str, Any]):
        """Print stock header with basic info.

        Args:
            ticker: Stock ticker symbol
            info: Stock information dictionary
        """
        company_name = info.get('longName', ticker)
        sector = info.get('sector', 'N/A')
        industry = info.get('industry', 'N/A')
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')

        header_text = f"[bold cyan]{ticker}[/bold cyan] - {company_name}\n"
        header_text += f"Sector: {sector} | Industry: {industry}\n"
        header_text += f"Current Price: ${self._format_number(current_price, decimals=2)}"

        self.console.print(Panel(header_text, box=box.DOUBLE, border_style="cyan"))

    def print_composite_score(self, composite: Dict[str, Any]):
        """Print composite score summary.

        Args:
            composite: Composite analysis results
        """
        score = composite['composite_score']
        recommendation = composite['recommendation']
        momentum_score = composite['momentum_score']
        fundamental_score = composite['fundamental_score']
        confidence = composite['confidence']
        investment_style = composite['investment_style']

        score_color = self._get_score_color(score)

        # Create score table
        table = Table(title="📊 Composite Analysis", box=box.ROUNDED, show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan", width=25)
        table.add_column("Value", justify="right", width=20)

        table.add_row("Composite Score", f"[{score_color}]{score:.1f}/100[/{score_color}]")
        table.add_row("Recommendation", f"[bold {score_color}]{recommendation}[/bold {score_color}]")
        table.add_row("", "")
        table.add_row("Momentum Score", f"[{self._get_score_color(momentum_score)}]{momentum_score:.1f}/100[/{self._get_score_color(momentum_score)}]")
        table.add_row("Fundamental Score", f"[{self._get_score_color(fundamental_score)}]{fundamental_score:.1f}/100[/{self._get_score_color(fundamental_score)}]")
        table.add_row("", "")
        table.add_row("Investment Style", investment_style)
        table.add_row("Confidence", confidence)

        self.console.print(table)

    def print_momentum_details(self, momentum: Dict[str, Any]):
        """Print detailed momentum analysis.

        Args:
            momentum: Momentum analysis results
        """
        components = momentum.get('components', {})

        table = Table(title="📈 Momentum Analysis Details", box=box.ROUNDED, show_header=True, header_style="bold green")
        table.add_column("Indicator", style="cyan", width=30)
        table.add_column("Value", justify="right", width=20)
        table.add_column("Score", justify="right", width=15)

        # RSI
        rsi_value = components.get('rsi_value', 0)
        rsi_score = components.get('rsi_score', 0)
        table.add_row("RSI (14-period)", f"{rsi_value:.2f}", f"{rsi_score}/15")

        # MACD
        macd_score = components.get('macd_score', 0)
        table.add_row("MACD", "Signal", f"{macd_score}/15")

        # Moving Averages
        ma_score = components.get('moving_average_score', 0)
        table.add_row("Moving Averages", "Trend", f"{ma_score}/20")

        # Volume
        volume_score = components.get('volume_score', 0)
        table.add_row("Volume Trend", "Analysis", f"{volume_score}/15")

        # Price Momentum
        momentum_score = components.get('price_momentum_score', 0)
        table.add_row("Price Momentum", "Multi-period", f"{momentum_score}/20")

        # Trend Strength (ADX)
        trend_score = components.get('trend_strength_score', 0)
        adx = components.get('adx', 0)
        table.add_row("Trend Strength (ADX)", f"{adx:.1f}", f"{trend_score}/15")

        self.console.print(table)

        # Price momentum details
        price_momentum = components.get('price_momentum', {})
        if price_momentum:
            mom_table = Table(title="Price Momentum Returns", box=box.SIMPLE, show_header=True)
            mom_table.add_column("Period", style="cyan")
            mom_table.add_column("Return", justify="right")

            for period, return_val in price_momentum.items():
                color = "green" if return_val > 0 else "red"
                mom_table.add_row(
                    period.replace('_', ' ').title(),
                    f"[{color}]{return_val:+.2f}%[/{color}]"
                )

            self.console.print(mom_table)

    def print_fundamental_details(self, fundamental: Dict[str, Any]):
        """Print detailed fundamental analysis.

        Args:
            fundamental: Fundamental analysis results
        """
        components = fundamental.get('components', {})

        # Valuation Metrics
        valuation = components.get('valuation_metrics', {})
        val_table = Table(title="💰 Valuation Metrics", box=box.ROUNDED, show_header=True, header_style="bold yellow")
        val_table.add_column("Metric", style="cyan", width=25)
        val_table.add_column("Value", justify="right", width=20)

        val_table.add_row("P/E Ratio", self._format_number(valuation.get('pe_ratio')))
        val_table.add_row("Forward P/E", self._format_number(valuation.get('forward_pe')))
        val_table.add_row("PEG Ratio", self._format_number(valuation.get('peg_ratio')))
        val_table.add_row("P/B Ratio", self._format_number(valuation.get('pb_ratio')))
        val_table.add_row("P/S Ratio", self._format_number(valuation.get('ps_ratio')))
        val_table.add_row("EV/EBITDA", self._format_number(valuation.get('ev_to_ebitda')))
        val_table.add_row("Market Cap", self._format_number(valuation.get('market_cap'), prefix="$"))

        self.console.print(val_table)

        # Profitability Metrics
        profitability = components.get('profitability_metrics', {})
        prof_table = Table(title="📊 Profitability Metrics", box=box.ROUNDED, show_header=True, header_style="bold green")
        prof_table.add_column("Metric", style="cyan", width=25)
        prof_table.add_column("Value", justify="right", width=20)

        prof_table.add_row("Gross Margin", self._format_number(profitability.get('gross_margin'), suffix="%", decimals=1) if profitability.get('gross_margin') else "N/A")
        prof_table.add_row("Operating Margin", self._format_number(profitability.get('operating_margin'), suffix="%", decimals=1) if profitability.get('operating_margin') else "N/A")
        prof_table.add_row("Net Margin", self._format_number(profitability.get('net_margin'), suffix="%", decimals=1) if profitability.get('net_margin') else "N/A")
        prof_table.add_row("ROE", self._format_number(profitability.get('roe'), suffix="%", decimals=1) if profitability.get('roe') else "N/A")
        prof_table.add_row("ROA", self._format_number(profitability.get('roa'), suffix="%", decimals=1) if profitability.get('roa') else "N/A")
        prof_table.add_row("Earnings Growth", self._format_number(profitability.get('earnings_growth'), suffix="%", decimals=1) if profitability.get('earnings_growth') else "N/A")

        self.console.print(prof_table)

        # Financial Health
        health = components.get('financial_health_metrics', {})
        health_table = Table(title="💪 Financial Health", box=box.ROUNDED, show_header=True, header_style="bold blue")
        health_table.add_column("Metric", style="cyan", width=25)
        health_table.add_column("Value", justify="right", width=20)

        health_table.add_row("Debt-to-Equity", self._format_number(health.get('debt_to_equity')))
        health_table.add_row("Current Ratio", self._format_number(health.get('current_ratio')))
        health_table.add_row("Quick Ratio", self._format_number(health.get('quick_ratio')))
        health_table.add_row("Free Cash Flow", self._format_number(health.get('free_cash_flow'), prefix="$"))
        health_table.add_row("Operating Cash Flow", self._format_number(health.get('operating_cash_flow'), prefix="$"))

        self.console.print(health_table)

        # Growth Metrics
        growth = components.get('growth_metrics', {})
        growth_table = Table(title="🚀 Growth Metrics", box=box.ROUNDED, show_header=True, header_style="bold magenta")
        growth_table.add_column("Metric", style="cyan", width=25)
        growth_table.add_column("Value", justify="right", width=20)

        growth_table.add_row("Revenue Growth", self._format_number(growth.get('revenue_growth'), suffix="%", decimals=1) if growth.get('revenue_growth') else "N/A")
        growth_table.add_row("Earnings Growth", self._format_number(growth.get('earnings_growth'), suffix="%", decimals=1) if growth.get('earnings_growth') else "N/A")

        upside = growth.get('upside_potential')
        if upside:
            color = "green" if upside > 0 else "red"
            growth_table.add_row("Analyst Upside", f"[{color}]{upside:+.1f}%[/{color}]")

        growth_table.add_row("Target Price", self._format_number(growth.get('target_mean'), prefix="$"))

        self.console.print(growth_table)

    def print_signals(self, signals: Dict[str, Any]):
        """Print trading signals and warnings.

        Args:
            signals: Dictionary with signals
        """
        momentum_signals = signals.get('momentum_signals', [])
        fundamental_signals = signals.get('fundamental_signals', [])
        risk_warnings = signals.get('risk_warnings', [])

        if momentum_signals or fundamental_signals or risk_warnings:
            self.console.print("\n[bold]🎯 Signals & Alerts[/bold]")

            if momentum_signals:
                self.console.print("\n[cyan]Momentum Signals:[/cyan]")
                for signal in momentum_signals:
                    self.console.print(f"  • {signal}")

            if fundamental_signals:
                self.console.print("\n[green]Fundamental Signals:[/green]")
                for signal in fundamental_signals:
                    self.console.print(f"  • {signal}")

            if risk_warnings:
                self.console.print("\n[red]⚠️  Risk Warnings:[/red]")
                for warning in risk_warnings:
                    self.console.print(f"  • {warning}")

    def print_full_analysis(self, ticker: str, info: Dict[str, Any], analysis: Dict[str, Any]):
        """Print complete analysis report.

        Args:
            ticker: Stock ticker symbol
            info: Stock information
            analysis: Complete analysis results
        """
        self.console.print("\n")
        self.print_stock_header(ticker, info)
        self.console.print("\n")

        composite = analysis['composite_analysis']
        self.print_composite_score(composite)
        self.console.print("\n")

        self.print_momentum_details(analysis['momentum_details'])
        self.console.print("\n")

        self.print_fundamental_details(analysis['fundamental_details'])
        self.console.print("\n")

        self.print_signals(composite['signals'])
        self.console.print("\n")

    def print_comparison_table(self, comparisons: List[Dict[str, Any]]):
        """Print comparison table for multiple stocks.

        Args:
            comparisons: List of stock analysis results
        """
        table = Table(title="📊 Stock Comparison", box=box.DOUBLE, show_header=True, header_style="bold cyan")

        table.add_column("Ticker", style="bold cyan", width=10)
        table.add_column("Composite", justify="right", width=12)
        table.add_column("Momentum", justify="right", width=12)
        table.add_column("Fundamental", justify="right", width=12)
        table.add_column("Recommendation", width=15)
        table.add_column("Style", width=20)

        for item in comparisons:
            ticker = item['ticker']
            composite = item['analysis']['composite_analysis']

            score = composite['composite_score']
            momentum = composite['momentum_score']
            fundamental = composite['fundamental_score']
            recommendation = composite['recommendation']
            style = composite['investment_style']

            score_color = self._get_score_color(score)

            table.add_row(
                ticker,
                f"[{score_color}]{score:.1f}[/{score_color}]",
                f"{momentum:.1f}",
                f"{fundamental:.1f}",
                f"[{score_color}]{recommendation}[/{score_color}]",
                style
            )

        self.console.print(table)

    def export_to_json(self, data: Dict[str, Any], filename: str):
        """Export analysis to JSON file.

        Args:
            data: Data to export
            filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        self.console.print(f"\n[green]✓[/green] Exported to {filename}")
