from datetime import date

from metrics import calculate_mrr
from models import MRREntry, Subscription


def test_mrr_two_months_mrr() -> None:
    # C001 active Jan–Feb, C002 active Jan–Mar
    subscriptions = [
        Subscription(
            customer_id="C001",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 2, 29),
            plan="basic",
            monthly_price=100.0,
        ),
        Subscription(
            customer_id="C002",
            start_date=date(2024, 1, 15),
            end_date=date(2024, 3, 31),
            plan="pro",
            monthly_price=200.0,
        ),
    ]

    result = calculate_mrr(subscriptions, today=date(2024, 12, 31))

    assert result == [
        MRREntry(start_date=date(2024, 1, 1), end_date=date(2024, 1, 31), mrr=300.0),
        MRREntry(start_date=date(2024, 2, 1), end_date=date(2024, 2, 29), mrr=300.0),
        MRREntry(start_date=date(2024, 3, 1), end_date=date(2024, 3, 31), mrr=200.0),
    ]
