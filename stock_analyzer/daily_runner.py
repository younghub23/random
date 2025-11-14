#!/usr/bin/env python3
"""Automated daily stock analysis runner with email/file reporting."""
import sys
import os
from datetime import datetime
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from batch_analyzer import BatchStockAnalyzer
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


class DailyStockReport:
    """Automated daily stock analysis with reporting."""

    def __init__(self, config_file: str = "daily_config.json"):
        """Initialize daily reporter.

        Args:
            config_file: Path to configuration file
        """
        self.config = self._load_config(config_file)
        self.timestamp = datetime.now().strftime('%Y%m%d')
        self.output_dir = Path(self.config.get('output_directory', 'daily_reports'))
        self.output_dir.mkdir(exist_ok=True)

    def _load_config(self, config_file: str) -> dict:
        """Load configuration from file or return defaults."""
        default_config = {
            'universe': 'sp500',
            'max_stocks': 500,
            'min_score': 0,
            'delay': 0.5,
            'output_directory': 'daily_reports',
            'email_enabled': False,
            'email_from': '',
            'email_to': [],
            'email_password': '',
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'top_n_stocks': 20,
            'send_csv': True
        }

        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
                print("Using default configuration")

        return default_config

    def run_analysis(self):
        """Run the batch analysis."""
        print(f"\n{'='*80}")
        print(f"Daily Stock Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")

        # Initialize analyzer
        analyzer = BatchStockAnalyzer(use_cache=False, delay=self.config['delay'])

        # Get stock universe
        tickers = analyzer.get_stock_universe(self.config['universe'])
        print(f"Universe: {self.config['universe'].upper()} ({len(tickers)} stocks)")

        # Run analysis
        max_stocks = self.config.get('max_stocks')
        analyzer.analyze_universe(tickers, max_stocks=max_stocks)

        # Save results
        output_base = str(self.output_dir / f"daily_analysis_{self.timestamp}")
        analyzer.save_results(output_base)

        # Print summary to console
        analyzer.print_summary()

        return analyzer

    def generate_email_report(self, analyzer: BatchStockAnalyzer) -> str:
        """Generate HTML email report.

        Args:
            analyzer: BatchStockAnalyzer with results

        Returns:
            HTML email body
        """
        top_stocks = analyzer.get_top_stocks(self.config['top_n_stocks'])
        opportunities = analyzer.get_investment_opportunities()

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #34495e; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
                th {{ background-color: #3498db; color: white; padding: 10px; text-align: left; }}
                td {{ padding: 8px; border-bottom: 1px solid #ddd; }}
                tr:hover {{ background-color: #f5f5f5; }}
                .strong-buy {{ color: #27ae60; font-weight: bold; }}
                .buy {{ color: #2ecc71; }}
                .hold {{ color: #f39c12; }}
                .sell {{ color: #e74c3c; }}
                .score-high {{ color: #27ae60; font-weight: bold; }}
                .score-med {{ color: #f39c12; }}
                .score-low {{ color: #e74c3c; }}
                .summary {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>📊 Daily Stock Analysis Report</h1>
            <p><strong>Date:</strong> {datetime.now().strftime('%B %d, %Y')}</p>
            <p><strong>Universe:</strong> {self.config['universe'].upper()}</p>

            <div class="summary">
                <h2>Summary Statistics</h2>
                <p><strong>Stocks Analyzed:</strong> {len(analyzer.results)}</p>
                <p><strong>Average Composite Score:</strong> {sum(r['composite_score'] for r in analyzer.results) / len(analyzer.results):.2f}</p>
                <p><strong>Strong Buys:</strong> {len([r for r in analyzer.results if r['recommendation'] == 'Strong Buy'])}</p>
                <p><strong>Buys:</strong> {len([r for r in analyzer.results if r['recommendation'] == 'Buy'])}</p>
            </div>

            <h2>🏆 Top {self.config['top_n_stocks']} Stocks</h2>
            <table>
                <tr>
                    <th>Rank</th>
                    <th>Ticker</th>
                    <th>Company</th>
                    <th>Score</th>
                    <th>Momentum</th>
                    <th>Fundamental</th>
                    <th>Recommendation</th>
                    <th>Sector</th>
                </tr>
        """

        for i, (_, row) in enumerate(top_stocks.iterrows(), 1):
            score_class = 'score-high' if row['composite_score'] >= 75 else 'score-med' if row['composite_score'] >= 60 else 'score-low'
            rec_class = row['recommendation'].lower().replace(' ', '-')

            html += f"""
                <tr>
                    <td>{i}</td>
                    <td><strong>{row['ticker']}</strong></td>
                    <td>{row['company_name'][:30]}</td>
                    <td class="{score_class}">{row['composite_score']:.1f}</td>
                    <td>{row['momentum_score']:.1f}</td>
                    <td>{row['fundamental_score']:.1f}</td>
                    <td class="{rec_class}">{row['recommendation']}</td>
                    <td>{row['sector']}</td>
                </tr>
            """

        html += "</table>"

        # Add investment opportunities
        if opportunities.get('Strong Buys') is not None and not opportunities['Strong Buys'].empty:
            html += f"""
            <h2>💎 Strong Buy Opportunities ({len(opportunities['Strong Buys'])})</h2>
            <table>
                <tr>
                    <th>Ticker</th>
                    <th>Company</th>
                    <th>Score</th>
                    <th>Style</th>
                </tr>
            """

            for _, row in opportunities['Strong Buys'].head(10).iterrows():
                html += f"""
                <tr>
                    <td><strong>{row['ticker']}</strong></td>
                    <td>{row['company_name'][:40]}</td>
                    <td class="score-high">{row['composite_score']:.1f}</td>
                    <td>{row['investment_style']}</td>
                </tr>
                """

            html += "</table>"

        html += """
            <hr style="margin-top: 40px;">
            <p style="color: #7f8c8d; font-size: 12px;">
                <em>This report was generated automatically by the Stock Analyzer batch system.
                Data sources: Yahoo Finance. Not financial advice - for informational purposes only.</em>
            </p>
        </body>
        </html>
        """

        return html

    def send_email_report(self, analyzer: BatchStockAnalyzer):
        """Send email report with analysis results.

        Args:
            analyzer: BatchStockAnalyzer with results
        """
        if not self.config['email_enabled']:
            print("\nEmail reporting disabled in config")
            return

        print("\nSending email report...")

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.config['email_from']
            msg['To'] = ', '.join(self.config['email_to'])
            msg['Subject'] = f"📊 Daily Stock Analysis - {datetime.now().strftime('%Y-%m-%d')}"

            # Generate and attach HTML report
            html_body = self.generate_email_report(analyzer)
            msg.attach(MIMEText(html_body, 'html'))

            # Attach CSV file if enabled
            if self.config.get('send_csv', True):
                csv_file = self.output_dir / f"daily_analysis_{self.timestamp}_top50.csv"
                if csv_file.exists():
                    with open(csv_file, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename="{csv_file.name}"')
                        msg.attach(part)

            # Send email
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            server.starttls()
            server.login(self.config['email_from'], self.config['email_password'])
            server.send_message(msg)
            server.quit()

            print(f"✓ Email sent to {', '.join(self.config['email_to'])}")

        except Exception as e:
            print(f"✗ Failed to send email: {e}")

    def generate_text_summary(self, analyzer: BatchStockAnalyzer) -> str:
        """Generate text summary for file or console.

        Args:
            analyzer: BatchStockAnalyzer with results

        Returns:
            Text summary
        """
        top_stocks = analyzer.get_top_stocks(self.config['top_n_stocks'])

        summary = f"""
{'='*80}
DAILY STOCK ANALYSIS SUMMARY
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}

OVERVIEW:
- Universe: {self.config['universe'].upper()}
- Stocks Analyzed: {len(analyzer.results)}
- Average Composite Score: {sum(r['composite_score'] for r in analyzer.results) / len(analyzer.results):.2f}

RECOMMENDATIONS:
"""

        from collections import Counter
        rec_counts = Counter(r['recommendation'] for r in analyzer.results)
        for rec, count in sorted(rec_counts.items(), key=lambda x: x[1], reverse=True):
            pct = (count / len(analyzer.results)) * 100
            summary += f"  {rec}: {count} ({pct:.1f}%)\n"

        summary += f"\n{'='*80}\nTOP {self.config['top_n_stocks']} STOCKS\n{'='*80}\n\n"
        summary += f"{'Rank':<6}{'Ticker':<8}{'Score':<8}{'M':<6}{'F':<6}{'Recommendation':<15}{'Sector':<20}\n"
        summary += "-" * 80 + "\n"

        for i, (_, row) in enumerate(top_stocks.iterrows(), 1):
            summary += f"{i:<6}{row['ticker']:<8}{row['composite_score']:<8.1f}"
            summary += f"{row['momentum_score']:<6.0f}{row['fundamental_score']:<6.0f}"
            summary += f"{row['recommendation']:<15}{row['sector'][:19]:<20}\n"

        return summary

    def save_text_summary(self, analyzer: BatchStockAnalyzer):
        """Save text summary to file.

        Args:
            analyzer: BatchStockAnalyzer with results
        """
        summary = self.generate_text_summary(analyzer)
        summary_file = self.output_dir / f"daily_summary_{self.timestamp}.txt"

        with open(summary_file, 'w') as f:
            f.write(summary)

        print(f"\n✓ Text summary saved to {summary_file}")

    def run(self):
        """Run complete daily analysis workflow."""
        try:
            # Run analysis
            analyzer = self.run_analysis()

            # Save text summary
            self.save_text_summary(analyzer)

            # Send email if enabled
            self.send_email_report(analyzer)

            print("\n✅ Daily analysis complete!")

        except Exception as e:
            print(f"\n❌ Error during daily analysis: {e}")
            import traceback
            traceback.print_exc()
            raise


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Daily Stock Analysis Runner')
    parser.add_argument('--config', default='daily_config.json', help='Configuration file')

    args = parser.parse_args()

    reporter = DailyStockReport(config_file=args.config)
    reporter.run()


if __name__ == '__main__':
    main()
