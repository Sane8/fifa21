from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from fifa_cleaner.decorators import track_time
from fifa_cleaner.exceptions import DataFileError
from fifa_cleaner.strategies import HeightParser, HitsParser, MoneyParser, StarParser, WeightParser, clean_text_value


class PandasPlayerCleaner:
    def __init__(self, input_path: str | Path) -> None:
        self.input_path = Path(input_path)

    @track_time
    def clean(self) -> pd.DataFrame:
        if not self.input_path.exists():
            raise DataFileError(f"Input file was not found: {self.input_path}")

        try:
            df = pd.read_csv(self.input_path, low_memory=False)
        except Exception as exc:
            raise DataFileError(f"Cannot read dataset: {self.input_path}") from exc

        if "↓OVA" in df.columns:
            df = df.rename(columns={"↓OVA": "OVA"})

        keep_columns = [
            "ID",
            "Name",
            "LongName",
            "Nationality",
            "Age",
            "OVA",
            "POT",
            "Club",
            "Contract",
            "Positions",
            "Height",
            "Weight",
            "Preferred Foot",
            "Best Position",
            "Joined",
            "Value",
            "Wage",
            "Release Clause",
            "W/F",
            "SM",
            "IR",
            "Hits",
        ]
        df = df[[column for column in keep_columns if column in df.columns]].copy()

        text_columns = ["Name", "LongName", "Nationality", "Club", "Contract", "Positions", "Preferred Foot", "Best Position"]
        for column in text_columns:
            if column in df.columns:
                df[column] = df[column].apply(clean_text_value)

        df["Club"] = df["Club"].fillna("Free agent")
        df["Positions"] = df["Positions"].fillna("")

        int_columns = ["ID", "Age", "OVA", "POT"]
        for column in int_columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

        df["height_cm"] = df["Height"].apply(HeightParser().parse)
        df["weight_kg"] = df["Weight"].apply(WeightParser().parse)
        df["value_eur"] = df["Value"].apply(MoneyParser().parse)
        df["wage_eur"] = df["Wage"].apply(MoneyParser().parse)
        df["release_clause_eur"] = df["Release Clause"].apply(MoneyParser().parse)
        df["weak_foot"] = df["W/F"].apply(StarParser().parse)
        df["skill_moves"] = df["SM"].apply(StarParser().parse)
        df["international_reputation"] = df["IR"].apply(StarParser().parse)
        df["hits"] = df["Hits"].apply(HitsParser().parse)

        df["joined_date"] = pd.to_datetime(df["Joined"], errors="coerce")
        df["primary_position"] = df["Positions"].str.split(",").str[0].str.strip()
        df["growth"] = df["POT"] - df["OVA"]
        df["value_per_overall"] = (df["value_eur"] / df["OVA"]).round(2)

        contract_years = df["Contract"].str.findall(r"\b(20[0-9]{2})\b")
        df["contract_start_year"] = contract_years.apply(lambda years: int(years[0]) if years else pd.NA)
        df["contract_end_year"] = contract_years.apply(lambda years: int(years[-1]) if years else pd.NA)
        df["contract_type"] = "unknown"
        df.loc[df["Contract"].str.lower().eq("free"), "contract_type"] = "free"
        df.loc[df["Contract"].str.lower().str.contains("loan", na=False), "contract_type"] = "loan"
        df.loc[df["contract_end_year"].notna() & df["contract_type"].eq("unknown"), "contract_type"] = "active"

        df["release_clause_eur"] = df["release_clause_eur"].fillna(0)
        df = df.dropna(subset=["ID", "Name", "Age", "OVA", "POT", "height_cm", "weight_kg"])
        df = df[(df["Age"] >= 16) & (df["Age"] <= 50) & (df["OVA"] >= 40)]

        rename_map = {
            "ID": "id",
            "Name": "name",
            "LongName": "long_name",
            "Nationality": "nationality",
            "Age": "age",
            "OVA": "overall",
            "POT": "potential",
            "Club": "club",
            "Contract": "contract",
            "Positions": "positions",
            "Preferred Foot": "preferred_foot",
            "Best Position": "best_position",
        }
        df = df.rename(columns=rename_map)

        result_columns = [
            "id",
            "name",
            "long_name",
            "nationality",
            "age",
            "overall",
            "potential",
            "growth",
            "club",
            "contract",
            "contract_type",
            "contract_start_year",
            "contract_end_year",
            "positions",
            "primary_position",
            "preferred_foot",
            "best_position",
            "height_cm",
            "weight_kg",
            "value_eur",
            "wage_eur",
            "release_clause_eur",
            "weak_foot",
            "skill_moves",
            "international_reputation",
            "hits",
            "joined_date",
            "value_per_overall",
        ]
        return df[result_columns].reset_index(drop=True)

    def save_cleaned(self, output_path: str | Path) -> pd.DataFrame:
        cleaned = self.clean()
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cleaned.to_csv(output_path, index=False)
        return cleaned

    def save_report(self, cleaned: pd.DataFrame, output_path: str | Path) -> dict:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        report = {
            "players_count": int(len(cleaned)),
            "average_overall": round(float(cleaned["overall"].mean()), 2),
            "average_age": round(float(cleaned["age"].mean()), 2),
            "most_expensive_player": str(cleaned.sort_values("value_eur", ascending=False).iloc[0]["name"]),
            "top_nationalities": cleaned["nationality"].value_counts().head(10).to_dict(),
            "top_positions": cleaned["primary_position"].value_counts().head(10).to_dict(),
        }

        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return report
