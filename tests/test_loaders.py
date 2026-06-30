from datetime import date
from pathlib import Path

from loaders import load_subscriptions


def test_load_price_word(tmp_path: Path) -> None:
    csv = tmp_path / "subs.csv"
    csv.write_text(
        "customer_id,start_date,end_date,plan,monthly_price\n"
        'C021,2024-08-02,,basic,"thirty"\n'
    )

    result = load_subscriptions(str(csv))

    assert len(result) == 1
    assert result[0].customer_id == "C021"
    assert result[0].monthly_price == 30.0


def test_load_date_with_whitespace(tmp_path: Path) -> None:
    csv = tmp_path / "subs.csv"
    csv.write_text(
        "customer_id,start_date,end_date,plan,monthly_price\n"
        'C028," 2024-10-14 ",,basic,30\n'
    )

    result = load_subscriptions(str(csv))

    assert len(result) == 1
    assert result[0].customer_id == "C028"
    assert result[0].start_date == date(2024, 10, 14)
