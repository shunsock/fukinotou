from pathlib import Path
from typing import List, Type, TypeVar, Generic
import polars
import pandas
import json
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class JsonlLoadResult(BaseModel, Generic[T]):
    """
    Model representing the result of loading a JSONL file.

    Attributes:
        path: Path to the loaded file
        values: List of parsed model instances (one per line)
    """

    path: Path
    values: List[T]

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
        if not self.values:
            # Return an empty DataFrame if there are no rows
            return polars.DataFrame()

        # Convert each model to a dict
        data_dicts = [row.model_dump() for row in self.values]

        # Create a DataFrame from the list of dicts
        df = polars.DataFrame(data_dicts)

        # Add path column if requested
        if include_path_as_column:
            path_str = str(self.path)
            df = df.with_columns(polars.lit(path_str).alias("path"))

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
        if not self.values:
            # Return an empty DataFrame if there are no rows
            return pandas.DataFrame()

        # Convert each model to a dict
        data_dicts = [row.model_dump() for row in self.values]

        # Create a DataFrame from the list of dicts
        df = pandas.DataFrame(data_dicts)

        # Add path column if requested
        if include_path_as_column:
            df["path"] = str(self.path)

        return df


class JsonlLoader(Generic[T]):
    """
    Loader for JSONL (JSON Lines) files that parses each line into the specified Pydantic model.

    This loader reads a JSONL file line by line, parses each valid JSON line, and validates
    it against the provided Pydantic model. Empty lines are skipped. The loader will raise
    exceptions for file not found, invalid paths, and JSON parsing errors.
    """

    def __init__(self, file_path: str | Path, model: Type[T]) -> None:
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not p.is_file():
            raise ValueError(f"Input path is a directory, not a file: {file_path}")
        self.file_path = p
        self.model = model

    def load(self) -> JsonlLoadResult[T]:
        """
        Load and parse the JSONL file into model instances.

        This method reads the JSONL file, parses each non-empty line as JSON,
        validates it against the specified Pydantic model, and returns
        a JsonlLoadResult containing the file path and a list of all
        successfully parsed model instances.

        Returns:
            JsonlLoadResult[T]: Result object containing the file path and list of model instances

        Raises:
            ValueError: If any line contains invalid JSON or fails model validation
        """
        values: List[T] = []
        with self.file_path.open("r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, start=1):
                raw = line.strip()
                if not raw:
                    continue  # skip empty lines
                try:
                    obj = json.loads(raw)
                except json.JSONDecodeError as e:
                    raise ValueError(
                        f"Invalid JSON on line {lineno} of {self.file_path}: {e}"
                    ) from e
                parsed = self.model.model_validate(obj)
                values.append(parsed)

        return JsonlLoadResult(path=self.file_path, values=values)
