class FifaCleanerError(Exception):
    """Base exception for project errors."""


class DataFileError(FifaCleanerError):
    """Raised when the input file cannot be read correctly."""


class ParseValueError(FifaCleanerError):
    """Raised when a dirty field value cannot be converted."""
