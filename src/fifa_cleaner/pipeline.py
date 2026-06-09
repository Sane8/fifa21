from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterator

from fifa_cleaner.decorators import track_time
from fifa_cleaner.exceptions import DataFileError, ParseValueError
from fifa_cleaner.strategies import PlayerNormalizer


class PlayerDataSource:
    def __init__(self, csv_path: str | Path) -> None:
        self.csv_path = Path(csv_path)

    def __iter__(self) -> Iterator[dict[str, str]]:
        if not self.csv_path.exists():
            raise DataFileError(f"Input file was not found: {self.csv_path}")

        try:
            with self.csv_path.open("r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                if not reader.fieldnames:
                    raise DataFileError(f"Input file has no header: {self.csv_path}")
                for row in reader:
                    yield row
        except UnicodeDecodeError as exc:
            raise DataFileError(f"Cannot read CSV as UTF-8: {self.csv_path}") from exc
        except csv.Error as exc:
            raise DataFileError(f"Broken CSV format: {self.csv_path}") from exc


class PlayerRowCleaner:
    def __init__(self, rows, normalizer: PlayerNormalizer | None = None, strict: bool = False) -> None:
        self.rows = rows
        self.normalizer = normalizer or PlayerNormalizer(strict=strict)
        self.skipped_rows = 0

    def __iter__(self) -> Iterator[dict]:
        for row in self.rows:
            try:
                yield self.normalizer.normalize_row(row)
            except ParseValueError:
                self.skipped_rows += 1


class PlayerRatingFilter:
    def __init__(self, rows, min_overall: int = 75, max_age: int | None = None) -> None:
        self.rows = rows
        self.min_overall = min_overall
        self.max_age = max_age

    def __iter__(self) -> Iterator[dict]:
        for row in self.rows:
            overall = row.get("overall")
            age = row.get("age")
            if overall is None or overall < self.min_overall:
                continue
            if self.max_age is not None and (age is None or age > self.max_age):
                continue
            yield row


class CsvExporter:
    @track_time
    def export(self, rows, output_path: str | Path) -> int:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        count = 0
        fieldnames: list[str] | None = None

        with output_path.open("w", encoding="utf-8", newline="") as file:
            writer = None
            for row in rows:
                if fieldnames is None:
                    fieldnames = list(row.keys())
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    writer.writeheader()
                writer.writerow(row)
                count += 1

        return count
