from __future__ import annotations

import json
import sys

from loaders import load_customers, load_subscriptions
from metrics import calculate_churn, calculate_cohort_retention, calculate_mrr


def main() -> None:
    if len(sys.argv) != 4:
        print("Usage: main.py <customers.csv> <subscriptions.csv> <output.json>")
        sys.exit(1)

    _, customers_path, subscriptions_path, output_path = sys.argv

    customers = load_customers(customers_path)
    subscriptions = load_subscriptions(subscriptions_path)

    mrr_by_month = {e.start_date: e for e in calculate_mrr(subscriptions)}
    churn_by_month = {e.start_date: e for e in calculate_churn(subscriptions)}
    cohort_by_month = {e.start_date: e for e in calculate_cohort_retention(customers, subscriptions)}

    all_months = sorted(set(mrr_by_month) | set(churn_by_month) | set(cohort_by_month))
    output = [
        {
            "start_date": month.isoformat(),
            "end_date": (mrr_by_month.get(month) or churn_by_month.get(month) or cohort_by_month[month]).end_date.isoformat(),
            "mrr": mrr_by_month[month].mrr if month in mrr_by_month else 0.0,
            "churned_customers": churn_by_month[month].churned_customers if month in churn_by_month else 0,
            "cohort": cohort_by_month[month].cohort if month in cohort_by_month else 0,
            "active_after_3_months": cohort_by_month[month].active_after_3_months if month in cohort_by_month else 0,
            "retention_rate_3_months": cohort_by_month[month].retention_rate_3_months if month in cohort_by_month else 0.0,
        }
        for month in all_months
    ]

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Written {len(output)} entries to {output_path}")


if __name__ == "__main__":
    main()
