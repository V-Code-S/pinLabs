import csv
import time
from pathlib import Path

import requests


API_URL = "http://localhost:8000/api/transactions"
DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "sample_transactions.csv"


def main():
    with DATA_FILE.open() as file_obj:
        reader = csv.DictReader(file_obj)
        for row in reader:
            payload = {
                "merchant_id": row["merchant_id"],
                "amount": float(row["amount"]),
                "category": row["category"],
                "channel": row["channel"],
                "created_at": row["created_at"],
                "language": "hi",
            }
            response = requests.post(API_URL, json=payload, timeout=10)
            print(response.json())
            time.sleep(1.5)


if __name__ == "__main__":
    main()
