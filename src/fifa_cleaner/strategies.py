from __future__ import annotations

import re
from abc import ABC, abstractmethod
from math import isnan
from typing import Any

from fifa_cleaner.exceptions import ParseValueError


class ParseStrategy(ABC):
    @abstractmethod
    def parse(self, value: Any) -> Any:
        raise NotImplementedError


def is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and isnan(value):
        return True
    return str(value).strip() in {"", "nan", "<NA>", "None"}


def clean_text_value(value: Any) -> str | None:
    if is_blank(value):
        return None

    text = str(value).replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    if not text:
        return None

    if "\u00c3" in text or "\u00c2" in text:
        try:
            text = text.encode("latin1").decode("utf-8")
        except UnicodeError:
            pass

    return text


class IntegerParser(ParseStrategy):
    def __init__(self, field_name: str = "value") -> None:
        self.field_name = field_name

    def parse(self, value: Any) -> int | None:
        if is_blank(value):
            return None
        try:
            return int(float(str(value).strip()))
        except ValueError as exc:
            raise ParseValueError(f"Cannot parse {self.field_name}: {value!r}") from exc


class MoneyParser(ParseStrategy):
    def parse(self, value: Any) -> int | None:
        if is_blank(value):
            return None

        text = str(value).strip()
        if text in {"-", "€-", "€0", "0"}:
            return 0

        match = re.fullmatch(r"€?\s*([0-9]+(?:\.[0-9]+)?)([MK])?", text, flags=re.IGNORECASE)
        if not match:
            raise ParseValueError(f"Cannot parse money value: {value!r}")

        number = float(match.group(1))
        suffix = (match.group(2) or "").upper()
        if suffix == "M":
            number *= 1_000_000
        elif suffix == "K":
            number *= 1_000

        return int(round(number))


class HeightParser(ParseStrategy):
    def parse(self, value: Any) -> int | None:
        if is_blank(value):
            return None

        text = str(value).strip().lower()
        cm_match = re.fullmatch(r"([0-9]+)\s*cm", text)
        if cm_match:
            return int(cm_match.group(1))

        feet_match = re.fullmatch(r"([0-9]+)'([0-9]+)\"", text)
        if feet_match:
            feet = int(feet_match.group(1))
            inches = int(feet_match.group(2))
            return round((feet * 12 + inches) * 2.54)

        raise ParseValueError(f"Cannot parse height: {value!r}")


class WeightParser(ParseStrategy):
    def parse(self, value: Any) -> int | None:
        if is_blank(value):
            return None

        text = str(value).strip().lower()
        kg_match = re.fullmatch(r"([0-9]+)\s*kg", text)
        if kg_match:
            return int(kg_match.group(1))

        lbs_match = re.fullmatch(r"([0-9]+)\s*lbs?", text)
        if lbs_match:
            return round(int(lbs_match.group(1)) * 0.453592)

        raise ParseValueError(f"Cannot parse weight: {value!r}")


class StarParser(ParseStrategy):
    def parse(self, value: Any) -> int | None:
        if is_blank(value):
            return None

        match = re.search(r"[0-9]+", str(value))
        if not match:
            raise ParseValueError(f"Cannot parse star rating: {value!r}")
        return int(match.group(0))


class HitsParser(ParseStrategy):
    def parse(self, value: Any) -> int | None:
        if is_blank(value):
            return None

        text = str(value).strip()
        match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)(K)?", text, flags=re.IGNORECASE)
        if not match:
            raise ParseValueError(f"Cannot parse hits: {value!r}")

        number = float(match.group(1))
        if match.group(2):
            number *= 1_000
        return int(round(number))


class PlayerNormalizer:
    def __init__(self, strict: bool = True) -> None:
        self.strict = strict
        self.parsers: dict[str, tuple[str, ParseStrategy]] = {
            "Age": ("age", IntegerParser("age")),
            "↓OVA": ("overall", IntegerParser("overall")),
            "OVA": ("overall", IntegerParser("overall")),
            "POT": ("potential", IntegerParser("potential")),
            "Height": ("height_cm", HeightParser()),
            "Weight": ("weight_kg", WeightParser()),
            "Value": ("value_eur", MoneyParser()),
            "Wage": ("wage_eur", MoneyParser()),
            "Release Clause": ("release_clause_eur", MoneyParser()),
            "W/F": ("weak_foot", StarParser()),
            "SM": ("skill_moves", StarParser()),
            "IR": ("international_reputation", StarParser()),
            "Hits": ("hits", HitsParser()),
        }

    def normalize_row(self, row: dict[str, Any]) -> dict[str, Any]:
        cleaned: dict[str, Any] = {
            "id": row.get("ID"),
            "name": self._clean_text(row.get("Name")),
            "long_name": self._clean_text(row.get("LongName")),
            "nationality": self._clean_text(row.get("Nationality")),
            "club": self._clean_text(row.get("Club")) or "Free agent",
            "positions": self._clean_text(row.get("Positions")),
            "preferred_foot": self._clean_text(row.get("Preferred Foot")),
            "best_position": self._clean_text(row.get("Best Position")),
        }

        positions = cleaned["positions"] or ""
        cleaned["primary_position"] = positions.split(",")[0].strip() if positions else None

        for source_name, (target_name, parser) in self.parsers.items():
            if source_name not in row:
                continue
            try:
                cleaned[target_name] = parser.parse(row.get(source_name))
            except ParseValueError:
                if self.strict:
                    raise
                cleaned[target_name] = None

        self._add_contract_fields(row.get("Contract"), cleaned)

        overall = cleaned.get("overall")
        potential = cleaned.get("potential")
        value = cleaned.get("value_eur")
        if isinstance(overall, int) and isinstance(potential, int):
            cleaned["growth"] = potential - overall
        else:
            cleaned["growth"] = None

        if isinstance(value, int) and isinstance(overall, int) and overall > 0:
            cleaned["value_per_overall"] = round(value / overall, 2)
        else:
            cleaned["value_per_overall"] = None

        return cleaned

    def _add_contract_fields(self, contract: Any, cleaned: dict[str, Any]) -> None:
        text = self._clean_text(contract) or ""
        cleaned["contract"] = text

        years = [int(year) for year in re.findall(r"\b(20[0-9]{2})\b", text)]
        cleaned["contract_start_year"] = years[0] if len(years) >= 1 else None
        cleaned["contract_end_year"] = years[-1] if len(years) >= 1 else None

        if "loan" in text.lower():
            cleaned["contract_type"] = "loan"
        elif text.lower() == "free":
            cleaned["contract_type"] = "free"
        elif years:
            cleaned["contract_type"] = "active"
        else:
            cleaned["contract_type"] = "unknown"

    @staticmethod
    def _clean_text(value: Any) -> str | None:
        return clean_text_value(value)
