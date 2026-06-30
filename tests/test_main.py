import json
from pathlib import Path
from unittest.mock import patch

from freezegun import freeze_time


@freeze_time("2024-03-31")
def test_end_to_end(tmp_path: Path) -> None:
    customers_csv = tmp_path / "customers.csv"
    customers_csv.write_text(
        "customer_id,signup_date,country\n"
        "C001,2024-01-01,NL\n"
        "C002,2024-01-01,DE\n"
    )

    subscriptions_csv = tmp_path / "subscriptions.csv"
    subscriptions_csv.write_text(
        "customer_id,start_date,end_date,plan,monthly_price\n"
        "C001,2024-01-01,2024-01-31,basic,100\n"  # ends Jan; gap to Mar 1 = 30 days → churn
        "C001,2024-03-01,,pro,200\n"
        "C002,2024-01-01,,basic,50\n"  # open-ended, no churn
    )

    output_json = tmp_path / "output.json"

    with patch("sys.argv", ["main.py", str(customers_csv), str(subscriptions_csv), str(output_json)]):
        from main import main
        main()

    result = json.loads(output_json.read_text())

    assert len(result) == 3  # Jan, Feb, Mar

    jan, feb, mar = result

    assert jan["start_date"] == "2024-01-01"
    assert jan["end_date"] == "2024-01-31"
    assert jan["mrr"] == 150.0           # C001 (100) + C002 (50)
    assert jan["churned_customers"] == 1  # C001 churns (30-day gap)

    assert feb["mrr"] == 50.0            # only C002
    assert feb["churned_customers"] == 0

    assert mar["mrr"] == 250.0           # C001 back (200) + C002 (50)
    assert mar["churned_customers"] == 0
