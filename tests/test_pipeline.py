import itertools

import pytest

from fifa_cleaner.decorators import track_time
from fifa_cleaner.exceptions import DataFileError
from fifa_cleaner.pipeline import CsvExporter, PlayerDataSource, PlayerRatingFilter, PlayerRowCleaner


def test_missing_source_file_raises_custom_exception(tmp_path):
    source = PlayerDataSource(tmp_path / "missing.csv")

    with pytest.raises(DataFileError):
        next(iter(source))


def test_data_source_is_lazy_iterable(sample_csv):
    source = PlayerDataSource(sample_csv)
    iterator = iter(source)

    first_row = next(iterator)

    assert first_row["Name"] == "A. Player"
    assert hasattr(iterator, "__next__")


def test_row_cleaner_transforms_rows_lazily(sample_csv):
    cleaned_rows = PlayerRowCleaner(PlayerDataSource(sample_csv))
    first_row = next(iter(cleaned_rows))

    assert first_row["club"] == "Test FC"
    assert first_row["value_eur"] == 50_000_000
    assert first_row["primary_position"] == "ST"


def test_rating_filter_keeps_only_matching_players(sample_csv):
    rows = PlayerRowCleaner(PlayerDataSource(sample_csv))
    filtered = PlayerRatingFilter(rows, min_overall=80, max_age=25)

    result = list(filtered)

    assert len(result) == 1
    assert result[0]["name"] == "A. Player"


@pytest.mark.integration
def test_exporter_saves_result(sample_csv, tmp_path):
    rows = PlayerRatingFilter(PlayerRowCleaner(PlayerDataSource(sample_csv)), min_overall=80)
    output_path = tmp_path / "filtered.csv"

    count = CsvExporter().export(rows, output_path)

    assert count == 1
    assert output_path.exists()
    assert "A. Player" in output_path.read_text(encoding="utf-8")


def test_track_time_decorator_stores_last_runtime():
    @track_time
    def take_three_items():
        return list(itertools.islice(range(10), 3))

    assert take_three_items() == [0, 1, 2]
    assert take_three_items.last_seconds is not None
    assert take_three_items.last_seconds >= 0
