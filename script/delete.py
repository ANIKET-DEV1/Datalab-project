import os
import time
from datetime import datetime

# Locate project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Chart image folder
CHARTS_DIR = os.path.join(BASE_DIR, 'core', 'static', 'charts')

# Delete files older than 1 hour (3600 seconds)
AGE_LIMIT = 3600

now = time.time()
deleted = 0

if os.path.exists(CHARTS_DIR):
    for filename in os.listdir(CHARTS_DIR):
        file_path = os.path.join(CHARTS_DIR, filename)
        if os.path.isfile(file_path):
            if now - os.path.getmtime(file_path) > AGE_LIMIT:
                os.remove(file_path)
                deleted += 1

print(f"[{datetime.now()}] Deleted {deleted} old chart(s).")
