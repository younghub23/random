"""Data caching system to minimize API calls."""
import json
import pickle
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional
import hashlib


class DataCache:
    """Simple file-based cache for stock data."""

    def __init__(self, cache_dir: Path, expiry_hours: int = 24):
        """Initialize the cache.

        Args:
            cache_dir: Directory to store cache files
            expiry_hours: Hours before cached data expires
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.expiry_hours = expiry_hours

    def _get_cache_path(self, key: str) -> Path:
        """Generate cache file path from key.

        Args:
            key: Cache key (e.g., 'AAPL_price_data')

        Returns:
            Path to cache file
        """
        # Hash the key to create a valid filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.pkl"

    def _is_expired(self, cache_path: Path) -> bool:
        """Check if cache file has expired.

        Args:
            cache_path: Path to cache file

        Returns:
            True if expired or doesn't exist
        """
        if not cache_path.exists():
            return True

        file_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        expiry_time = datetime.now() - timedelta(hours=self.expiry_hours)

        return file_time < expiry_time

    def get(self, key: str) -> Optional[Any]:
        """Retrieve data from cache.

        Args:
            key: Cache key

        Returns:
            Cached data or None if not found/expired
        """
        cache_path = self._get_cache_path(key)

        if self._is_expired(cache_path):
            return None

        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Warning: Failed to load cache for {key}: {e}")
            return None

    def set(self, key: str, data: Any) -> bool:
        """Store data in cache.

        Args:
            key: Cache key
            data: Data to cache

        Returns:
            True if successful
        """
        cache_path = self._get_cache_path(key)

        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            return True
        except Exception as e:
            print(f"Warning: Failed to cache data for {key}: {e}")
            return False

    def invalidate(self, key: str) -> bool:
        """Remove data from cache.

        Args:
            key: Cache key

        Returns:
            True if file was deleted
        """
        cache_path = self._get_cache_path(key)

        if cache_path.exists():
            try:
                cache_path.unlink()
                return True
            except Exception as e:
                print(f"Warning: Failed to delete cache for {key}: {e}")
                return False

        return False

    def clear_all(self) -> int:
        """Clear all cached data.

        Returns:
            Number of files deleted
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                cache_file.unlink()
                count += 1
            except Exception:
                pass

        return count

    def get_cache_info(self) -> dict:
        """Get information about the cache.

        Returns:
            Dictionary with cache statistics
        """
        cache_files = list(self.cache_dir.glob("*.pkl"))
        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            'num_files': len(cache_files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_dir': str(self.cache_dir)
        }
