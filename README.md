# utilus-exercise

A data exercise that calculates MRR, churn, and cohort retention from customer and subscription CSV files.

## Setup

```bash
uv sync --dev
```

## Run

```bash
uv run python main.py customers.csv subscriptions.csv output.json
```

## Test

```bash
uv run pytest
```

## Lint

```bash
just lint
```
