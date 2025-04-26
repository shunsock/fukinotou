import csv
from pathlib import Path
from typing import Dict, List, Type, TypeVar, Generic

import polars
import pandas
from pydantic import BaseModel

from .load_error import LoadingError

T = TypeVar("T", bound=BaseModel)


class CsvRowLoadResult(BaseModel, Generic[T]):
    """Model representing a single row loaded from a CSV file.

    Attributes:
        path: Path to the CSV file from which this row was loaded
        row: The parsed and validated row data as a model instance
    """

    path: Path
    row: T


class CsvLoadResult(BaseModel, Generic[T]):
    """Model representing the result of loading an entire CSV file.

    Attributes:
        path: Path to the loaded file
        value: List of row results
    """

    path: Path
    value: List[CsvRowLoadResult[T]]

    def to_polars(self, include_path_as_column: bool = False) -> polars.DataFrame:
        """Convert the result to a Polars DataFrame.

        This method converts all model instances in the result to a Polars DataFrame.
        Each row in the DataFrame represents one model instance.

        Args:
            include_path_as_column: If True, adds a 'path' column with the file path
                                    for each row. Default is False.

        Returns:
            Polars DataFrame containing the model data
        """
        if not self.value:
            return polars.DataFrame()

        data_dicts = [row.row.model_dump() for row in self.value]
        df = polars.DataFrame(data_dicts)

        if include_path_as_column:
            df = df.with_columns(polars.lit(str(self.path)).alias("path"))

        return df

    def to_pandas(self, include_path_as_column: bool = False) -> pandas.DataFrame:
        """Convert the result to a Pandas DataFrame.

        This method converts all model instances in the result to a Pandas DataFrame.
        Each row in the DataFrame represents one model instance.

        Args:
            include_path_as_column: If True, adds a 'path' column with the file path
                                    for each row. Default is False.

        Returns:
            Pandas DataFrame containing the model data
        """
        if not self.value:
            return pandas.DataFrame()

        data_dicts = [row.row.model_dump() for row in self.value]
        df = pandas.DataFrame(data_dicts)

        if include_path_as_column:
            df["path"] = str(self.path)

        return df


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

    def load(self, path: str | Path, encoding: str = "utf-8") -> CsvLoadResult[T]:
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
        if not p.exists():
            raise LoadingError(f"File not found: {p}")
        if not p.is_file():
            raise LoadingError(f"Input path is a directory: {p}")

        csv_rows: List[CsvRowLoadResult[T]] = []
        with p.open("r", encoding=encoding) as f:
            reader = csv.reader(f)

            # Header is required
            try:
                headers = next(reader)
            except StopIteration:
                raise LoadingError(
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
                    model_instance = self.model(**row_dict)
                except Exception as e:
                    raise LoadingError(
                        original_exception=e,
                        error_message=f"Error parsing row {row_number} in {p}: {e}",
                    )

                csv_rows.append(CsvRowLoadResult(path=p, row=model_instance))

        return CsvLoadResult(path=p, value=csv_rows)
