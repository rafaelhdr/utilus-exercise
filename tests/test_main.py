import json
from pathlib import Path
from unittest.mock import patch

import pytest
from freezegun import freeze_time


@freeze_time("2024-04-30")
def test_end_to_end(tmp_path: Path) -> None:
    customers_csv = tmp_path / "customers.csv"
    customers_csv.write_text(
        "customer_id,signup_date,country\n"
        "C001,2024-01-01,NL\n"
        "C002,2024-01-01,DE\n"
        "C003,2024-01-01,FR\n"  # churns before April → not counted in active_after_3_months
    )

    subscriptions_csv = tmp_path / "subscriptions.csv"
    subscriptions_csv.write_text(
        "customer_id,start_date,end_date,plan,monthly_price\n"
        "C001,2024-01-01,2024-01-31,basic,100\n"  # 30-day gap to Mar 1 → churn
        "C001,2024-03-01,,pro,200\n"
        "C002,2024-01-01,,basic,50\n"
        "C003,2024-01-01,2024-02-28,basic,50\n"   # ends Feb, no comeback → inactive in April
    )

    output_json = tmp_path / "output.json"

    with patch("sys.argv", ["main.py", str(customers_csv), str(subscriptions_csv), str(output_json)]):
        from main import main
        main()

    result = json.loads(output_json.read_text())

    assert len(result) == 4  # Jan, Feb, Mar, Apr

    jan = result[0]
    assert jan["start_date"] == "2024-01-01"
    assert jan["mrr"] == 200.0            # C001 (100) + C002 (50) + C003 (50)
    assert jan["churned_customers"] == 1  # C001 (30-day gap)
    assert jan["cohort"] == 3
    assert jan["active_after_3_months"] == 2          # C001 (back Mar) + C002; C003 inactive
    assert jan["retention_rate_3_months"] == pytest.approx(2 / 3)
