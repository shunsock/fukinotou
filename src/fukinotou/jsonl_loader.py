from pathlib import Path
from typing import List, Type, TypeVar, Generic
import polars
import pandas
import json
from pydantic import BaseModel, ValidationError

from fukinotou.load_error import LoadingError

T = TypeVar("T", bound=BaseModel)


class JsonlRowLoadResult(BaseModel, Generic[T]):
    """Model representing a single row loaded from a JSONL file.

    Attributes:
        path: Path to the JSONL file from which this row was loaded
        row: The parsed and validated row data as a model instance
    """

    path: Path
    row: T


class JsonlLoadResult(BaseModel, Generic[T]):
    """Model representing the result of loading an entire JSONL file.

    Attributes:
        path: Path to the loaded file
        value: List of row results
    """

    path: Path
    value: List[JsonlRowLoadResult[T]]

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


class JsonlLoader(Generic[T]):
    """Generic JSONL file loader that validates rows against a Pydantic model.

    This loader reads a JSONL file and converts each row into instances of a specified
    Pydantic model, performing validation during the conversion process.

    Type Parameters:
        T: A Pydantic BaseModel subclass that defines the schema for JSONL rows
    """

    def __init__(self, model: Type[T]) -> None:
        """Initialize the JSONL loader with a target model class.

        Args:
            model: The Pydantic model class used to validate and parse JSONL rows
        """
        self.model = model

    def load(self, path: str | Path, encoding: str = "utf-8") -> JsonlLoadResult[T]:
        """Load and validate data from a JSONL file.

        Reads a JSONL file, validates each row against the provided model class,
        and returns a structured result containing all valid rows.

        The JSONL file must have a header row. Empty lines are skipped during processing.

        Args:
            path: Path to the JSONL file (string or Path object)
            encoding: Character encoding of the JSONL file (defaults to "utf-8")

        Returns:
            JsonlLoadResult containing the validated rows as model instances

        Raises:
            LoadingError: If the file doesn't exist, is a directory, has no headers,
                          or contains rows that fail validation
        """
        p = Path(path)
        if not p.exists():
            raise LoadingError(f"File not found: {p}")
        if not p.is_file():
            raise LoadingError(f"Input path is a directory: {p}")

        jsonl_rows: List[JsonlRowLoadResult[T]] = []
        try:
            f = p.open(mode="r", encoding=encoding)
            for lineno, line in enumerate(f, start=1):
                raw = line.strip()

                # Skip empty lines
                if not raw:
                    continue

                # Validation
                try:
                    obj = json.loads(raw)
                    parsed: T = self.model.model_validate(obj)
                except json.JSONDecodeError as e:
                    raise LoadingError(
                        original_exception=e,
                        error_message=f"Error parsing JSON on line {lineno} of {p}: {e}",
                    )
                except ValidationError as e:
                    raise LoadingError(
                        original_exception=e,
                        error_message=f"Error validating row {lineno} of {p}: {e}",
                    )

                jsonl_rows.append(JsonlRowLoadResult(path=p, row=parsed))
        except FileNotFoundError as e:
            raise LoadingError(
                original_exception=e, error_message=f"Error reading file {p}: {e}"
            )

        return JsonlLoadResult(path=p, value=jsonl_rows)
