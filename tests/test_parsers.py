import pytest

from fifa_cleaner.exceptions import ParseValueError
from fifa_cleaner.strategies import HeightParser, HitsParser, MoneyParser, PlayerNormalizer, WeightParser


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("€50M", 50_000_000),
        ("€103.5M", 103_500_000),
        ("€560K", 560_000),
        ("€0", 0),
    ],
)
def test_money_parser_handles_fifa_values(raw_value, expected):
    assert MoneyParser().parse(raw_value) == expected


@pytest.mark.parametrize(
    ("parser", "raw_value", "expected"),
    [
        (HeightParser(), "183cm", 183),
        (HeightParser(), "6'0\"", 183),
        (WeightParser(), "75kg", 75),
        (WeightParser(), "165lbs", 75),
        (HitsParser(), "1.2K", 1200),
    ],
)
def test_other_dirty_values_are_parsed(parser, raw_value, expected):
    assert parser.parse(raw_value) == expected


def test_invalid_money_value_raises_custom_exception():
    with pytest.raises(ParseValueError):
        MoneyParser().parse("many euros")


def test_normalizer_uses_strategy_objects_for_fields():
    row = {
        "ID": "10",
        "Name": "T. Student",
        "LongName": "Test Student",
        "Nationality": "Portugal",
        "Club": "\n\nCollege FC",
        "Positions": "CM, CDM",
        "Age": "20",
        "↓OVA": "70",
        "POT": "81",
        "Height": "180cm",
        "Weight": "70kg",
        "Value": "€1M",
        "Wage": "€5K",
        "Release Clause": "€2M",
    }

    cleaned = PlayerNormalizer().normalize_row(row)

    assert cleaned["value_eur"] == 1_000_000
    assert cleaned["height_cm"] == 180
    assert cleaned["primary_position"] == "CM"
    assert cleaned["growth"] == 11
