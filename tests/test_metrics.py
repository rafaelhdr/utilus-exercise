from datetime import date

from freezegun import freeze_time

from metrics import calculate_churn, calculate_cohort_retention, calculate_mrr
from models import Customer, MRREntry, Subscription


class TestMRR:
    def test_two_subscriptions(self) -> None:
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

    def test_gap_between_subscriptions(self) -> None:
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
    def test_open_ended_subscription(self) -> None:
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


class TestChurn:
    def test_gap_less_than_30_days_is_not_churn(self) -> None:
        # End Jan 31, next starts Feb 15: gap = 15 days < 30 → not a churn
        subscriptions = [
            Subscription(customer_id="C001", start_date=date(2024, 1, 1), end_date=date(2024, 1, 31), plan="basic", monthly_price=30.0),
            Subscription(customer_id="C001", start_date=date(2024, 2, 15), end_date=None, plan="pro", monthly_price=50.0),
        ]

        result = calculate_churn(subscriptions, today=date(2024, 3, 31))

        assert all(e.churned_customers == 0 for e in result)

    def test_gap_of_30_days_is_churn(self) -> None:
        # End Jan 31, next starts Mar 1: gap = 30 days → churn in January
        subscriptions = [
            Subscription(customer_id="C001", start_date=date(2024, 1, 1), end_date=date(2024, 1, 31), plan="basic", monthly_price=30.0),
            Subscription(customer_id="C001", start_date=date(2024, 3, 1), end_date=None, plan="pro", monthly_price=50.0),
        ]

        result = calculate_churn(subscriptions, today=date(2024, 3, 31))

        january = next(e for e in result if e.start_date == date(2024, 1, 1))
        assert january.churned_customers == 1


class TestCohortRetention:
    def _make_sub(self, customer_id: str, start: date, end: date | None, price: float = 100.0) -> Subscription:
        return Subscription(customer_id=customer_id, start_date=start, end_date=end, plan="basic", monthly_price=price)

    def _make_customer(self, customer_id: str, signup: date) -> Customer:
        return Customer(customer_id=customer_id, signup_date=signup)

    def test_all_retained_after_3_months(self) -> None:
        customers = [
            self._make_customer("C001", date(2024, 1, 1)),
            self._make_customer("C002", date(2024, 1, 15)),
        ]
        subscriptions = [
            self._make_sub("C001", date(2024, 1, 1), None),
            self._make_sub("C002", date(2024, 1, 1), None),
        ]

        result = calculate_cohort_retention(customers, subscriptions, today=date(2024, 4, 30))

        jan = next(e for e in result if e.start_date == date(2024, 1, 1))
        assert jan.cohort == 2
        assert jan.active_after_3_months == 2
        assert jan.retention_rate_3_months == 1.0

    def test_zero_active_when_3_month_window_not_reached(self) -> None:
        # Today is still within the same month as signup; 3-month window is in the future
        customers = [self._make_customer("C001", date(2024, 1, 1))]
        subscriptions = [self._make_sub("C001", date(2024, 1, 1), None)]  # open-ended

        result = calculate_cohort_retention(customers, subscriptions, today=date(2024, 1, 31))

        jan = next(e for e in result if e.start_date == date(2024, 1, 1))
        assert jan.active_after_3_months == 0
        assert jan.retention_rate_3_months == 0.0

    def test_partial_retention_after_3_months(self) -> None:
        customers = [
            self._make_customer("C001", date(2024, 1, 1)),
            self._make_customer("C002", date(2024, 1, 1)),
        ]
        subscriptions = [
            self._make_sub("C001", date(2024, 1, 1), None),
            self._make_sub("C002", date(2024, 1, 1), date(2024, 2, 28)),  # churns before April
        ]

        result = calculate_cohort_retention(customers, subscriptions, today=date(2024, 4, 30))

        jan = next(e for e in result if e.start_date == date(2024, 1, 1))
        assert jan.cohort == 2
        assert jan.active_after_3_months == 1
        assert jan.retention_rate_3_months == 0.5
