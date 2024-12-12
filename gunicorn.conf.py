import os

port = int(os.environ.get("PORT", 10000))
workers = 4
bind = f"0.0.0.0:{port}"
timeout = 120
