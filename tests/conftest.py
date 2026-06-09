import csv

import pytest


@pytest.fixture
def sample_csv(tmp_path):
    path = tmp_path / "players.csv"
    rows = [
        {
            "ID": "1",
            "Name": "A. Player",
            "LongName": "Alex Player",
            "Nationality": "Spain",
            "Age": "21",
            "↓OVA": "82",
            "POT": "88",
            "Club": "\n\nTest FC",
            "Contract": "2019 ~ 2024",
            "Positions": "ST, LW",
            "Height": "183cm",
            "Weight": "75kg",
            "Preferred Foot": "Right",
            "Best Position": "ST",
            "Value": "€50M",
            "Wage": "€90K",
            "Release Clause": "€95.5M",
            "W/F": "4 ★",
            "SM": "3★",
            "IR": "2 ★",
            "Hits": "1.2K",
        },
        {
            "ID": "2",
            "Name": "B. Player",
            "LongName": "Bob Player",
            "Nationality": "France",
            "Age": "31",
            "↓OVA": "72",
            "POT": "72",
            "Club": "",
            "Contract": "Free",
            "Positions": "CB",
            "Height": "190cm",
            "Weight": "84kg",
            "Preferred Foot": "Left",
            "Best Position": "CB",
            "Value": "€2.5M",
            "Wage": "€12K",
            "Release Clause": "€0",
            "W/F": "2 ★",
            "SM": "2★",
            "IR": "1 ★",
            "Hits": "15",
        },
    ]

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    return path
