from pathlib import Path
from typing import List, Type, TypeVar, Generic
import json
from pydantic import BaseModel, ValidationError

from fukinotou.dataframe_exportable import DataframeExportable
from fukinotou.exception.loading_error import LoadingError

T = TypeVar("T", bound=BaseModel)


class JsonlRow(BaseModel, Generic[T]):
    """Model representing a single row loaded from a JSONL file.

    Attributes:
        path: Path to the JSONL file from which this row was loaded
        value: The parsed and validated row data as a model instance
    """

    path: Path
    value: T


class JsonlLoaded(BaseModel, Generic[T], DataframeExportable):
    """Model representing the result of loading an entire JSONL file.

    Attributes:
        path: Path to the loaded file
        value: List of rows
    """

    path: Path
    value: List[JsonlRow[T]]


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

    def load(self, path: str | Path, encoding: str = "utf-8") -> JsonlLoaded[T]:
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
        if not p.is_file():
            raise LoadingError(f"Input path is invalid: {p}")

        jsonl_rows: List[JsonlRow[T]] = []
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

                jsonl_rows.append(JsonlRow(path=p, value=parsed))
        except FileNotFoundError as e:
            raise LoadingError(
                original_exception=e, error_message=f"Error reading file {p}: {e}"
            )

        return JsonlLoaded(path=p, value=jsonl_rows)
