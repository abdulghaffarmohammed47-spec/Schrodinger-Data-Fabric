import sys
try:
    import fastapi
    import uvicorn
    import sklearn
    import Crypto
    import firebase_admin
    import pandas
    import numpy
    print("All imports successful!")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)
