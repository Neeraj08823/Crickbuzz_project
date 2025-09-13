import os
import requests
import json
from dotenv import load_dotenv
from datetime import datetime
import time

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_HOST = os.getenv("API_HOST")

CACHE_DIR = os.path.join(os.path.dirname(__file__), 'cache')
LOG_DIR = os.path.join(os.path.dirname(__file__), 'logs')

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "fetch_warnings.log")

def log_warning(message: str):
    """Append a warning or skipped data entry to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"⚠️ {message}")

def fetch_with_cache(endpoint, filename, retries=3, backoff=2):
    """
    Fetch data from API with caching and retry logic.
    Logs warnings for failures.
    """
    cache_path = os.path.join(CACHE_DIR, filename)

    # ✅ Use cache if already exists
    if os.path.exists(cache_path):
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    url = f"https://{API_HOST}/{endpoint}"

    attempt = 0
    while attempt < retries:
        try:
            headers = {"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": API_HOST}
            response = requests.get(url, headers=headers, timeout=10)

            # Handle quota exceeded
            if response.status_code == 429:
                log_warning(f"Quota exceeded for {endpoint} (API key ending {API_KEY[-5:]})")
                return {}

            response.raise_for_status()
            data = response.json()

            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            print(f"✅ Cached {filename}")
            return data

        except (requests.RequestException, ValueError) as e:
            attempt += 1
            wait_time = backoff ** attempt
            log_warning(f"Attempt {attempt} failed for {endpoint} with error: {e}")

            if attempt < retries:
                print(f"⏳ Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                log_warning(f"❌ Failed after {retries} attempts: {endpoint}")
                return {}