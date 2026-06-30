from __future__ import annotations

from datetime import date

import pandas as pd

from models import MRREntry, Subscription


def calculate_mrr(
    subscriptions: list[Subscription],
    today: date | None = None,
) -> list[MRREntry]:
    if today is None:
        today = date.today()

    if not subscriptions:
        return []

    all_dates: list[date] = [s.start_date for s in subscriptions]
    all_dates += [s.end_date for s in subscriptions if s.end_date is not None]

    min_date = min(all_dates)
    end_date = min(today, max(all_dates))

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
