import polars as pl
from pathlib import Path
from typing import List, Type, TypeVar, Generic

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class ParquetRowLoadResult(BaseModel, Generic[T]):
    """
    Model representing the result of loading a single Parquet row.

    Attributes:
        path: Path to the loaded Parquet file
        value: Single row parsed as a model instance
    """

    path: Path
    value: T


class ParquetLoadResult(BaseModel, Generic[T]):
    """
    Model representing the result of loading an entire Parquet file.

    Attributes:
        path: Path to the loaded Parquet file
        value: List of row load results, each containing a model instance
    """

    path: Path
    value: List[ParquetRowLoadResult[T]]


class ParquetLoader(Generic[T]):
    """
    Loader for Parquet files that parses rows into the specified Pydantic model.

    This loader uses Polars to read Parquet files and converts each row into
    an instance of the provided Pydantic model. The loader will raise
    exceptions for file not found and invalid paths.
    """

    def __init__(self, path: str | Path, model: Type[T]) -> None:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not p.is_file():
            raise ValueError(f"Input path is directory path: {path}")
        self.file_path = p
        self.model = model

    def load(self) -> ParquetLoadResult[T]:
        """
        Load and parse the Parquet file into model instances.

        This method reads the Parquet file using Polars, converts each row
        into a Pydantic model instance, and returns a ParquetLoadResult
        containing the file path and a list of row results with model instances.

        Returns:
            ParquetLoadResult[T]: Result object containing the file path and list of row results

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If a row fails model validation
        """
        df = pl.read_parquet(self.file_path)

        results: List[ParquetRowLoadResult[T]] = []
        for row_dict in df.to_dicts():
            # Filter out None values to use model defaults instead
            cleaned_dict = {k: v for k, v in row_dict.items() if v is not None}
            model_instance = self.model(**cleaned_dict)
            results.append(
                ParquetRowLoadResult(path=self.file_path, value=model_instance)
            )

        return ParquetLoadResult(path=self.file_path, value=results)
