from __future__ import annotations

import json
import sys

from loaders import load_subscriptions
from metrics import calculate_mrr


def main() -> None:
    if len(sys.argv) != 4:
        print("Usage: main.py <customers.csv> <subscriptions.csv> <output.json>")
        sys.exit(1)

    _, __, subscriptions_path, output_path = sys.argv

    subscriptions = load_subscriptions(subscriptions_path)
    mrr_entries = calculate_mrr(subscriptions)

    output = [
        {
            "start_date": entry.start_date.isoformat(),
            "end_date": entry.end_date.isoformat(),
            "mrr": entry.mrr,
        }
        for entry in mrr_entries
    ]

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Written {len(output)} entries to {output_path}")


if __name__ == "__main__":
    main()
