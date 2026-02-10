"""Test config loading."""
try:
    from src.config import settings
    print(f"✓ Config loaded successfully!")
    print(f"Database URL: {settings.database_url}")
except Exception as e:
    print(f"✗ Error loading config:")
    import traceback
    traceback.print_exc()
