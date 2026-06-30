from __future__ import annotations

from collections import defaultdict
from datetime import date

import pandas as pd

from models import ChurnEntry, MRREntry, Subscription

CHURN_GAP_DAYS = 30


def calculate_mrr(
    subscriptions: list[Subscription],
    today: date | None = None,
) -> list[MRREntry]:
    if today is None:
        today = date.today()

    if not subscriptions:
        return []

    min_date = min(s.start_date for s in subscriptions)
    effective_ends = [
        s.end_date if s.end_date is not None else today for s in subscriptions
    ]
    end_date = min(today, max(effective_ends))

    if end_date < min_date:
        return []

    month_starts = pd.date_range(
        start=date(min_date.year, min_date.month, 1),
        end=date(end_date.year, end_date.month, 1),
        freq="MS",
    )

    results: list[MRREntry] = []
    for ts in month_starts:
        month_start = ts.date()
        month_end = (ts + pd.DateOffset(months=1) - pd.Timedelta(days=1)).date()

        mrr = sum(
            sub.monthly_price
            for sub in subscriptions
            if sub.start_date <= month_end
            and (sub.end_date is None or sub.end_date >= month_start)
        )

        results.append(MRREntry(start_date=month_start, end_date=month_end, mrr=mrr))

    return results


def calculate_churn(
    subscriptions: list[Subscription],
    today: date | None = None,
) -> list[ChurnEntry]:
    if today is None:
        today = date.today()

    if not subscriptions:
        return []

    by_customer: dict[str, list[Subscription]] = defaultdict(list)
    for sub in subscriptions:
        by_customer[sub.customer_id].append(sub)

    churn_dates: list[date] = []
    for subs in by_customer.values():
        subs_sorted = sorted(subs, key=lambda s: s.start_date)
        for sub in subs_sorted:
            if sub.end_date is None:
                continue
            next_subs = [s for s in subs_sorted if s.start_date > sub.end_date]
            if next_subs:
                nearest_start = min(next_subs, key=lambda s: s.start_date).start_date
                if (nearest_start - sub.end_date).days < CHURN_GAP_DAYS:
                    continue
            churn_dates.append(sub.end_date)

    min_date = min(s.start_date for s in subscriptions)
    effective_ends = [s.end_date if s.end_date is not None else today for s in subscriptions]
    end_date = min(today, max(effective_ends))

    if end_date < min_date:
        return []

    month_starts = pd.date_range(
        start=date(min_date.year, min_date.month, 1),
        end=date(end_date.year, end_date.month, 1),
        freq="MS",
    )

    results: list[ChurnEntry] = []
    for ts in month_starts:
        month_start = ts.date()
        month_end = (ts + pd.DateOffset(months=1) - pd.Timedelta(days=1)).date()

        count = sum(1 for d in churn_dates if month_start <= d <= month_end)
        results.append(ChurnEntry(start_date=month_start, end_date=month_end, churned_customers=count))

    return results
