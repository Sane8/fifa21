from pathlib import Path
import sys


BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR / "src"))

from fifa_cleaner.pandas_processing import PandasPlayerCleaner
from fifa_cleaner.pipeline import CsvExporter, PlayerDataSource, PlayerRatingFilter, PlayerRowCleaner

DATA_PATH = BASE_DIR / "data" / "fifa21_raw_data_v2.csv"
OUTPUTS_DIR = BASE_DIR / "outputs"


def main() -> None:
    cleaner = PandasPlayerCleaner(DATA_PATH)
    cleaned = cleaner.save_cleaned(OUTPUTS_DIR / "fifa21_cleaned.csv")
    cleaner.save_report(cleaned, OUTPUTS_DIR / "report.json")

    source = PlayerDataSource(DATA_PATH)
    cleaned_rows = PlayerRowCleaner(source, strict=False)
    strong_young_players = PlayerRatingFilter(cleaned_rows, min_overall=85, max_age=25)
    exported_count = CsvExporter().export(strong_young_players, OUTPUTS_DIR / "young_top_players_lazy.csv")

    print(f"Saved cleaned dataset: {OUTPUTS_DIR / 'fifa21_cleaned.csv'}")
    print(f"Saved report: {OUTPUTS_DIR / 'report.json'}")
    print(f"Saved lazy pipeline result: {exported_count} rows")


if __name__ == "__main__":
    main()
