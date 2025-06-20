import os

bind = f"127.0.0.1:{os.environ.get('PORT', '8000')}"
workers = 2
