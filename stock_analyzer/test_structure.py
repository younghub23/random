"""Test script to validate code structure without API calls."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    try:
        from utils.config import Config
        print("✓ Config module imported")
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        return False

    try:
        from data.cache import DataCache
        print("✓ Cache module imported")
    except Exception as e:
        print(f"✗ Cache import failed: {e}")
        return False

    try:
        from utils.output import OutputFormatter
        print("✓ Output module imported")
    except Exception as e:
        print(f"✗ Output import failed: {e}")
        return False

    # Test that we can create instances
    try:
        cache = DataCache('.test_cache', 24)
        print("✓ DataCache instance created")
    except Exception as e:
        print(f"✗ DataCache instantiation failed: {e}")
        return False

    try:
        formatter = OutputFormatter()
        print("✓ OutputFormatter instance created")
    except Exception as e:
        print(f"✗ OutputFormatter instantiation failed: {e}")
        return False

    # Test config validation
    try:
        Config.validate()
        print("✓ Config validation passed")
    except Exception as e:
        print(f"✗ Config validation failed: {e}")
        return False

    print("\n✅ All structural tests passed!")
    return True

if __name__ == '__main__':
    success = test_imports()
    sys.exit(0 if success else 1)
