import csv
import json
import os
import pandas as pd

DATA_DIR = "./" # Directory to store data files

def save_market_data_csv(data, filename="market_data.csv.csv"):
    filepath = os.path.join(DATA_DIR, filename)
    print(f"Attempting to save market data to: {os.path.abspath(filepath)}")
    try:
        df = pd.DataFrame(data)
        df.to_csv(filepath, mode='a', header=not os.path.exists(filepath), index=False)
    except Exception as e:
        print(f"Error saving market data to CSV: {e}")

def save_news_data_json(news_data, filename="news_data.json.json"):
    filepath = os.path.join(DATA_DIR, filename)
    print(f"Attempting to save news data to: {os.path.abspath(filepath)}")
    try:
        with open(filepath, 'a') as f:
            json.dump(news_data, f, indent=4)
            f.write('\n') # Add a newline for better readability if appending
    except Exception as e:
        print(f"Error saving news data to JSON: {e}")

def load_market_data_csv(filename="market_data.csv.csv"):
    filepath = os.path.join(DATA_DIR, filename)
    try:
        if os.path.exists(filepath):
            return pd.read_csv(filepath)
        else:
            return pd.DataFrame()
    except FileNotFoundError:
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading market data from CSV: {e}")
        return pd.DataFrame()

def load_news_data_json(filename="news_data.json.json"):
    filepath = os.path.join(DATA_DIR, filename)
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return [json.loads(line) for line in f]
        else:
            return []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in news data: {e}")
        return []
    except Exception as e:
        print(f"Error loading news data from JSON: {e}")
        return []