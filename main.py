from __future__ import annotations

import json
import sys

from loaders import load_subscriptions
from metrics import calculate_churn, calculate_mrr


def main() -> None:
    if len(sys.argv) != 4:
        print("Usage: main.py <customers.csv> <subscriptions.csv> <output.json>")
        sys.exit(1)

    _, __, subscriptions_path, output_path = sys.argv

    subscriptions = load_subscriptions(subscriptions_path)
    mrr_entries = {e.start_date: e for e in calculate_mrr(subscriptions)}
    churn_entries = {e.start_date: e for e in calculate_churn(subscriptions)}

    all_months = sorted(set(mrr_entries) | set(churn_entries))
    output = [
        {
            "start_date": month.isoformat(),
            "end_date": (mrr_entries.get(month) or churn_entries[month]).end_date.isoformat(),
            "mrr": mrr_entries[month].mrr if month in mrr_entries else 0.0,
            "churned_customers": churn_entries[month].churned_customers if month in churn_entries else 0,
        }
        for month in all_months
    ]

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Written {len(output)} entries to {output_path}")


if __name__ == "__main__":
    main()
