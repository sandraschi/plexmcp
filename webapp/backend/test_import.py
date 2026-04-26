import sys

print(f"Python path: {sys.path}")
try:
    from app import main

    print("Import successful")
except ImportError as e:
    print(f"Import failed: {e}")
except Exception as e:
    print(f"Error: {e}")
