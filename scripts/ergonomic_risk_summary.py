"""Summarize the ergonomic risk measures from my tea-picker assessment."""
from __future__ import annotations
import argparse
import json
import pandas as pd

REQUIRED = {"task", "rula", "reba", "niosh_lifting_index"}

def risk_label(rula: float, reba: float, lifting_index: float) -> str:
    if rula >= 7 or reba >= 11 or lifting_index > 3:
        return "very_high"
    if rula >= 5 or reba >= 8 or lifting_index > 1:
        return "high"
    if rula >= 3 or reba >= 4:
        return "moderate"
    return "low"

def summarize(path: str) -> list[dict]:
    frame = pd.read_csv(path)
    if missing := REQUIRED.difference(frame.columns):
        raise ValueError(f"Missing columns: {sorted(missing)}")
    results = []
    for row in frame.itertuples(index=False):
        results.append({"task": row.task, "rula": float(row.rula), "reba": float(row.reba),
                        "niosh_lifting_index": float(row.niosh_lifting_index),
                        "priority": risk_label(float(row.rula), float(row.reba),
                                               float(row.niosh_lifting_index))})
    return sorted(results, key=lambda item: (item["priority"], item["task"]))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv")
    args = parser.parse_args()
    print(json.dumps(summarize(args.csv), indent=2))
