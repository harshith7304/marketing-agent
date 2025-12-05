"""
Analyze datasets in documents folder for marketing agent
"""
import pandas as pd
import json
import os

print("=" * 60)
print("DATASET ANALYSIS FOR MARKETING AGENT")
print("=" * 60)

# 1. Facebook
print("\n--- FACEBOOK ---")
df = pd.read_csv('./data/documents/Facebook-datasets.csv', nrows=100)
print(f"Total columns: {len(df.columns)}")
print(f"Columns: {df.columns.tolist()}")
print(f"Useful for marketing: text, likes, comments, shares, engagement")

# 2. Instagram  
print("\n--- INSTAGRAM ---")
df = pd.read_csv('./data/documents/Instagram-datasets.csv', nrows=100)
print(f"Total columns: {len(df.columns)}")
print(f"Columns: {df.columns.tolist()}")

# 3. TikTok
print("\n--- TIKTOK ---")
df = pd.read_csv('./data/documents/TikTok-datasets.csv', nrows=100)
print(f"Total columns: {len(df.columns)}")
print(f"Columns: {df.columns.tolist()}")

# 4. Twitter
print("\n--- TWITTER ---")
df = pd.read_csv('./data/documents/Twitter- datasets.csv', nrows=100)
print(f"Total columns: {len(df.columns)}")
print(f"Columns: {df.columns.tolist()}")

# 5. LinkedIn
print("\n--- LINKEDIN ---")
with open('./data/documents/linkedin_ads.json', 'r') as f:
    data = json.load(f)
print(f"Total items: {len(data)}")
if len(data) > 0:
    print(f"Keys per item: {list(data[0].keys())}")
    print(f"Sample ad text: {data[0].get('adText', 'N/A')[:200]}")

print("\n" + "=" * 60)
print("RECOMMENDATION")
print("=" * 60)
