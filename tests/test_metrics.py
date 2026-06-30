from datetime import date

from freezegun import freeze_time

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


def test_mrr_gap_between_subscriptions() -> None:
    subscriptions = [
        Subscription(
            customer_id="C001",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 2, 29),
            plan="basic",
            monthly_price=100.0,
        ),
        Subscription(
            customer_id="C001",
            start_date=date(2024, 4, 1),
            end_date=date(2024, 5, 31),
            plan="basic",
            monthly_price=100.0,
        ),
    ]

    result = calculate_mrr(subscriptions, today=date(2024, 12, 31))

    assert result == [
        MRREntry(start_date=date(2024, 1, 1), end_date=date(2024, 1, 31), mrr=100.0),
        MRREntry(start_date=date(2024, 2, 1), end_date=date(2024, 2, 29), mrr=100.0),
        MRREntry(start_date=date(2024, 3, 1), end_date=date(2024, 3, 31), mrr=0.0),
        MRREntry(start_date=date(2024, 4, 1), end_date=date(2024, 4, 30), mrr=100.0),
        MRREntry(start_date=date(2024, 5, 1), end_date=date(2024, 5, 31), mrr=100.0),
    ]


@freeze_time("2024-06-30")
def test_mrr_open_ended_subscription() -> None:
    subscriptions = [
        Subscription(
            customer_id="C001",
            start_date=date(2024, 1, 1),
            end_date=None,
            plan="basic",
            monthly_price=100.0,
        ),
    ]

    result = calculate_mrr(subscriptions)

    assert result == [
        MRREntry(start_date=date(2024, 1, 1), end_date=date(2024, 1, 31), mrr=100.0),
        MRREntry(start_date=date(2024, 2, 1), end_date=date(2024, 2, 29), mrr=100.0),
        MRREntry(start_date=date(2024, 3, 1), end_date=date(2024, 3, 31), mrr=100.0),
        MRREntry(start_date=date(2024, 4, 1), end_date=date(2024, 4, 30), mrr=100.0),
        MRREntry(start_date=date(2024, 5, 1), end_date=date(2024, 5, 31), mrr=100.0),
        MRREntry(start_date=date(2024, 6, 1), end_date=date(2024, 6, 30), mrr=100.0),
    ]
