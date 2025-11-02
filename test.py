# test_imports.py
try:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from flask_bcrypt import Bcrypt
    from flask_cors import CORS
    import requests
    print("✅ All imports successful!")
except ImportError as e:
    print(f"❌ Import error: {e}")