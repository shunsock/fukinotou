import csv
from pathlib import Path
from typing import Dict, List, Type, TypeVar, Generic

from pydantic import BaseModel, ValidationError

from .exception.loading_exception import LoadingException
from .abstraction.dataframe_exportable import DataframeExportable

T = TypeVar("T", bound=BaseModel)


class CsvRow(BaseModel, Generic[T]):
    """Model representing a single row loaded from a CSV file.

    Attributes:
        path: Path to the CSV file from which this row was loaded
        value: The parsed and validated row data as a model instance
    """

    path: Path
    value: T


class CsvLoaded(BaseModel, Generic[T], DataframeExportable):
    """Model representing the result of loading an entire CSV file.

    Attributes:
        path: Path to the loaded file
        value: List of rows
    """

    path: Path
    value: List[CsvRow[T]]


class CsvLoader(Generic[T]):
    """Generic CSV file loader that validates rows against a Pydantic model.

    This loader reads a CSV file and converts each row into instances of a specified
    Pydantic model, performing validation during the conversion process.

    Type Parameters:
        T: A Pydantic BaseModel subclass that defines the schema for CSV rows
    """

    def __init__(self, model: Type[T]) -> None:
        """Initialize the CSV loader with a target model class.

        Args:
            model: The Pydantic model class used to validate and parse CSV rows
        """
        self.model = model

    def load(self, path: str | Path, encoding: str = "utf-8") -> CsvLoaded[T]:
        """Load and validate data from a CSV file.

        Reads a CSV file, validates each row against the provided model class,
        and returns a structured result containing all valid rows.

        The CSV file must have a header row. Empty lines are skipped during processing.

        Args:
            path: Path to the CSV file (string or Path object)
            encoding: Character encoding of the CSV file (defaults to "utf-8")

        Returns:
            CsvLoadResult containing the validated rows as model instances

        Raises:
            LoadingError: If the file doesn't exist, is a directory, has no headers,
                          or contains rows that fail validation
        """
        p = Path(path)
        if not p.is_file():
            raise LoadingException(f"Input path is invalid: {p}")

        csv_rows: List[CsvRow[T]] = []
        try:
            f = p.open("r", encoding=encoding)
            reader = csv.reader(f)

            # Header is required
            try:
                headers = next(reader)
            except StopIteration:
                raise LoadingException(
                    original_exception=None, error_message=f"No headers found in {p}"
                )

            # Validation foreach rows
            for row_number, row_data in enumerate(reader, start=2):
                # Skip empty lines
                if not any(cell.strip() for cell in row_data):
                    continue

                # Validation
                row_dict: Dict[str, str] = {}
                for i, header in enumerate(headers):
                    if i < len(row_data):
                        row_dict[header] = row_data[i]

                try:
                    model_instance = self.model.model_validate(row_dict)
                except ValidationError as e:
                    raise LoadingException(
                        original_exception=e,
                        error_message=f"Error parsing row {row_number} in {p}: {e}",
                    )

                csv_rows.append(CsvRow(path=p, value=model_instance))
        except Exception as e:
            raise LoadingException(
                original_exception=e, error_message=f"Error reading file {p}: {e}"
            )

        return CsvLoaded(path=p, value=csv_rows)
