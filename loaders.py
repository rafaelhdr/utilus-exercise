from __future__ import annotations

from datetime import date

import pandas as pd

from models import Customer, Subscription


def _parse_date(value: object) -> date | None:
    try:
        if pd.isna(value):  # type: ignore[arg-type]
            return None
    except (TypeError, ValueError):
        pass
    s = str(value).strip()
    if not s or s == "nan":
        return None
    return date.fromisoformat(s)


_PRICE_WORDS: dict[str, float] = {"thirty": 30}


def _parse_price(value: object) -> float:
    s = str(value).strip().lower()
    if s in _PRICE_WORDS:
        return _PRICE_WORDS[s]
    return float(s)


def load_customers(filepath: str) -> list[Customer]:
    df = pd.read_csv(filepath)
    customers: list[Customer] = []
    for _, row in df.iterrows():
        try:
            signup_date = _parse_date(row["signup_date"])
            if signup_date is None:
                continue
            country_val = row.get("country")
            country = str(country_val).strip() if pd.notna(country_val) else None
            customers.append(
                Customer(
                    customer_id=str(row["customer_id"]).strip(),
                    signup_date=signup_date,
                    country=country if country else None,
                )
            )
        except (ValueError, TypeError):
            continue
    return customers


def load_subscriptions(filepath: str) -> list[Subscription]:
    df = pd.read_csv(filepath)
    subscriptions: list[Subscription] = []
    for _, row in df.iterrows():
        try:
            start_date = _parse_date(row["start_date"])
            if start_date is None:
                continue

            end_date = _parse_date(row["end_date"])
            monthly_price = _parse_price(row["monthly_price"])

            if end_date is not None and end_date < start_date:
                continue

            subscriptions.append(
                Subscription(
                    customer_id=str(row["customer_id"]).strip(),
                    start_date=start_date,
                    end_date=end_date,
                    plan=str(row["plan"]).strip(),
                    monthly_price=monthly_price,
                )
            )
        except (ValueError, TypeError):
            continue
    return subscriptions
