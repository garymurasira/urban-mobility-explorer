"""Pipeline orchestrator.

Runs the data layer end to end:
    load -> integrate -> clean -> features -> export

Run from the repo root with:
    python -m data.src.pipeline

Raw input lives in data/raw/ (git-ignored); the cleaned full output and the
1k-row sample are written to data/processed/ and data/sample/ respectively.
"""

from data.src.load import load_trips
from data.src.integrate import integrate_zones
from data.src.clean import clean_trips
from data.src.features import add_features


def run():
    """Orchestrate the five pipeline stages.

    Intended flow (each step is a stub for now):
        1. load     — read raw trips CSV with typed schema
        2. integrate — join zone lookup + shapefile centroids
        3. clean    — handle missing/duplicate/outlier rows, log exclusions
        4. features — derive the contract's engineered columns
        5. export   — write cleaned dataset + 1k-row sample for the DB load
    """
    # 1. load
    trips = load_trips()
    # 2. integrate
    trips = integrate_zones(trips)
    # 3. clean
    trips = clean_trips(trips)
    # 4. features
    trips = add_features(trips)
    # 5. export
    # TODO: write data/processed/ full output + data/sample/ 1k-row sample
    return trips


if __name__ == "__main__":
    run()
