"""Momentum analysis using technical indicators."""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from utils.config import Config


class MomentumAnalyzer:
    """Analyzes stock momentum using technical indicators."""

    def __init__(self, price_data: pd.DataFrame):
        """Initialize momentum analyzer.

        Args:
            price_data: DataFrame with OHLCV data
        """
        self.df = price_data.copy()
        self.indicators = {}

    def calculate_sma(self, period: int) -> pd.Series:
        """Calculate Simple Moving Average.

        Args:
            period: Number of periods

        Returns:
            Series with SMA values
        """
        return self.df['Close'].rolling(window=period).mean()

    def calculate_ema(self, period: int) -> pd.Series:
        """Calculate Exponential Moving Average.

        Args:
            period: Number of periods

        Returns:
            Series with EMA values
        """
        return self.df['Close'].ewm(span=period, adjust=False).mean()

    def calculate_rsi(self, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index.

        Args:
            period: Number of periods (default 14)

        Returns:
            Series with RSI values
        """
        delta = self.df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def calculate_macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence).

        Args:
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period

        Returns:
            Dictionary with MACD line, signal line, and histogram
        """
        ema_fast = self.calculate_ema(fast)
        ema_slow = self.calculate_ema(slow)

        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line

        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }

    def calculate_bollinger_bands(self, period: int = 20, std_dev: int = 2) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands.

        Args:
            period: Number of periods
            std_dev: Number of standard deviations

        Returns:
            Dictionary with upper, middle, and lower bands
        """
        middle = self.calculate_sma(period)
        std = self.df['Close'].rolling(window=period).std()

        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)

        return {
            'upper': upper,
            'middle': middle,
            'lower': lower
        }

    def calculate_adx(self, period: int = 14) -> float:
        """Calculate Average Directional Index (trend strength).

        Args:
            period: Number of periods

        Returns:
            Latest ADX value
        """
        high = self.df['High']
        low = self.df['Low']
        close = self.df['Close']

        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Calculate Directional Movement
        up_move = high - high.shift()
        down_move = low.shift() - low

        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

        # Smooth the values
        atr = tr.rolling(window=period).mean()
        plus_di = 100 * (pd.Series(plus_dm).rolling(window=period).mean() / atr)
        minus_di = 100 * (pd.Series(minus_dm).rolling(window=period).mean() / atr)

        # Calculate DX and ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()

        return adx.iloc[-1] if len(adx) > 0 and not pd.isna(adx.iloc[-1]) else 0

    def analyze_volume_trend(self) -> Dict[str, Any]:
        """Analyze volume trends.

        Returns:
            Dictionary with volume analysis
        """
        recent_volume = self.df['Volume'].tail(20).mean()
        avg_volume = self.df['Volume'].mean()

        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1

        # Calculate price-volume correlation
        price_returns = self.df['Close'].pct_change()
        volume_changes = self.df['Volume'].pct_change()
        correlation = price_returns.corr(volume_changes)

        return {
            'recent_avg_volume': recent_volume,
            'overall_avg_volume': avg_volume,
            'volume_ratio': volume_ratio,
            'price_volume_correlation': correlation if not pd.isna(correlation) else 0
        }

    def calculate_price_momentum(self) -> Dict[str, float]:
        """Calculate price momentum over various periods.

        Returns:
            Dictionary with momentum metrics
        """
        current_price = self.df['Close'].iloc[-1]

        # Calculate returns over different periods
        returns = {}

        periods = {
            '1_month': 21,
            '3_month': 63,
            '6_month': 126,
            '12_month': 252
        }

        for name, days in periods.items():
            if len(self.df) >= days:
                old_price = self.df['Close'].iloc[-days]
                returns[name] = ((current_price - old_price) / old_price) * 100
            else:
                returns[name] = 0

        return returns

    def find_support_resistance(self) -> Dict[str, float]:
        """Find key support and resistance levels.

        Returns:
            Dictionary with support and resistance prices
        """
        # Use recent highs/lows for support/resistance
        recent_data = self.df.tail(60)

        resistance = recent_data['High'].max()
        support = recent_data['Low'].min()

        current_price = self.df['Close'].iloc[-1]

        return {
            'resistance': resistance,
            'support': support,
            'current_price': current_price,
            'distance_to_resistance': ((resistance - current_price) / current_price) * 100,
            'distance_to_support': ((current_price - support) / current_price) * 100
        }

    def get_momentum_score(self) -> Dict[str, Any]:
        """Calculate comprehensive momentum score (0-100).

        Returns:
            Dictionary with score and component analysis
        """
        scores = []
        components = {}

        # 1. Moving Average Analysis (0-20 points)
        sma_20 = self.calculate_sma(20).iloc[-1]
        sma_50 = self.calculate_sma(50).iloc[-1]
        sma_200 = self.calculate_sma(200).iloc[-1] if len(self.df) >= 200 else None
        current_price = self.df['Close'].iloc[-1]

        ma_score = 0
        if current_price > sma_20:
            ma_score += 7
        if current_price > sma_50:
            ma_score += 7
        if sma_200 is not None and current_price > sma_200:
            ma_score += 6

        scores.append(ma_score)
        components['moving_average_score'] = ma_score

        # 2. RSI Analysis (0-15 points)
        rsi = self.calculate_rsi(Config.RSI_PERIOD).iloc[-1]
        if 30 <= rsi <= 70:
            rsi_score = 15  # Healthy range
        elif 70 < rsi <= 80:
            rsi_score = 10  # Overbought but still positive
        elif 20 <= rsi < 30:
            rsi_score = 10  # Oversold but recovering
        elif rsi > 80:
            rsi_score = 5   # Very overbought
        else:
            rsi_score = 5   # Very oversold

        scores.append(rsi_score)
        components['rsi_score'] = rsi_score
        components['rsi_value'] = rsi

        # 3. MACD Analysis (0-15 points)
        macd_data = self.calculate_macd(Config.MACD_FAST, Config.MACD_SLOW, Config.MACD_SIGNAL)
        macd_line = macd_data['macd'].iloc[-1]
        signal_line = macd_data['signal'].iloc[-1]
        histogram = macd_data['histogram'].iloc[-1]

        macd_score = 0
        if macd_line > signal_line:
            macd_score += 8
        if histogram > 0:
            macd_score += 7

        scores.append(macd_score)
        components['macd_score'] = macd_score

        # 4. Volume Analysis (0-15 points)
        volume_analysis = self.analyze_volume_trend()
        volume_score = 0

        if volume_analysis['volume_ratio'] > 1.2:
            volume_score += 8
        elif volume_analysis['volume_ratio'] > 1.0:
            volume_score += 5

        if volume_analysis['price_volume_correlation'] > 0.3:
            volume_score += 7
        elif volume_analysis['price_volume_correlation'] > 0:
            volume_score += 3

        scores.append(volume_score)
        components['volume_score'] = volume_score

        # 5. Price Momentum (0-20 points)
        momentum = self.calculate_price_momentum()
        momentum_score = 0

        if momentum['1_month'] > 5:
            momentum_score += 5
        if momentum['3_month'] > 10:
            momentum_score += 5
        if momentum['6_month'] > 15:
            momentum_score += 5
        if momentum['12_month'] > 20:
            momentum_score += 5

        scores.append(momentum_score)
        components['price_momentum_score'] = momentum_score
        components['price_momentum'] = momentum

        # 6. Trend Strength (ADX) (0-15 points)
        adx = self.calculate_adx()
        if adx > 50:
            trend_score = 15
        elif adx > 25:
            trend_score = 10
        elif adx > 20:
            trend_score = 5
        else:
            trend_score = 0

        scores.append(trend_score)
        components['trend_strength_score'] = trend_score
        components['adx'] = adx

        # Calculate total score
        total_score = sum(scores)

        return {
            'score': total_score,
            'components': components,
            'current_price': current_price,
            'support_resistance': self.find_support_resistance()
        }
