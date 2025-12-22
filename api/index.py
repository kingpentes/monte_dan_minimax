import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import the Flask app from web/app.py
from web.app import app

# Export app for Vercel
app = app
