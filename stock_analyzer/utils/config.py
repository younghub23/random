"""Configuration management for the stock analyzer."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)


class Config:
    """Configuration settings for the stock analyzer."""

    # API Configuration
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
    FINANCIAL_MODELING_PREP_API_KEY = os.getenv('FINANCIAL_MODELING_PREP_API_KEY', '')

    # Cache Settings
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    CACHE_DIRECTORY = Path(os.getenv('CACHE_DIRECTORY', '.cache'))
    CACHE_EXPIRY_HOURS = int(os.getenv('CACHE_EXPIRY_HOURS', '24'))

    # Scoring Weights
    MOMENTUM_WEIGHT = float(os.getenv('MOMENTUM_WEIGHT', '0.4'))
    FUNDAMENTAL_WEIGHT = float(os.getenv('FUNDAMENTAL_WEIGHT', '0.6'))

    # Analysis Parameters
    DEFAULT_LOOKBACK_DAYS = int(os.getenv('DEFAULT_LOOKBACK_DAYS', '365'))
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', '14'))
    MACD_FAST = int(os.getenv('MACD_FAST', '12'))
    MACD_SLOW = int(os.getenv('MACD_SLOW', '26'))
    MACD_SIGNAL = int(os.getenv('MACD_SIGNAL', '9'))

    # Recommendation Thresholds
    STRONG_BUY_THRESHOLD = float(os.getenv('STRONG_BUY_THRESHOLD', '80'))
    BUY_THRESHOLD = float(os.getenv('BUY_THRESHOLD', '65'))
    HOLD_THRESHOLD = float(os.getenv('HOLD_THRESHOLD', '45'))
    SELL_THRESHOLD = float(os.getenv('SELL_THRESHOLD', '30'))

    @classmethod
    def get_recommendation(cls, score: float) -> str:
        """Convert a composite score to a recommendation."""
        if score >= cls.STRONG_BUY_THRESHOLD:
            return "Strong Buy"
        elif score >= cls.BUY_THRESHOLD:
            return "Buy"
        elif score >= cls.HOLD_THRESHOLD:
            return "Hold"
        elif score >= cls.SELL_THRESHOLD:
            return "Sell"
        else:
            return "Strong Avoid"

    @classmethod
    def validate(cls):
        """Validate configuration settings."""
        if not (0 <= cls.MOMENTUM_WEIGHT <= 1):
            raise ValueError("MOMENTUM_WEIGHT must be between 0 and 1")
        if not (0 <= cls.FUNDAMENTAL_WEIGHT <= 1):
            raise ValueError("FUNDAMENTAL_WEIGHT must be between 0 and 1")

        # Weights should sum to 1
        total_weight = cls.MOMENTUM_WEIGHT + cls.FUNDAMENTAL_WEIGHT
        if abs(total_weight - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")

        # Ensure cache directory exists if caching is enabled
        if cls.CACHE_ENABLED:
            cls.CACHE_DIRECTORY.mkdir(parents=True, exist_ok=True)

        return True


# Validate configuration on import
Config.validate()
