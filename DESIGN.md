# Design of the project

## How the code is structured
main.py is the entrypoint, which calls the metrics files
metrics.py are the logic behing the calculations, to get MRR, churn etc
loaders.py to load the csv files to be consumed, also cleaning the data if necessary
types.py are the types themselves

## How you modeled the business rules (MRR, churn, cohorts).
Each one of them is defined as a type in the types.py. We have entry for them.
To join the information, we use the same keys (the dates) and group for the json

## How you would add another metric in the future.
It is organized in the metrics.py. In case of a new metric, than we should add more
But in case it grows a lot, we should split it into metrics/[metric_x].py

## Any assumptions you made and known trade-offs.
The end date was set for today (in case of None end date). So, the json might be longer as expected.
This was a quick exercise. No github actions (like for lint) in order to keep it simple.
For logging, I just made a print for simplicity. Ideally, it could be written to file, and handled better. But this was just an exercise, and I didn't bother about it.
