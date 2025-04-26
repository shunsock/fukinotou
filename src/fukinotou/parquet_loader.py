import polars as pl
from pathlib import Path
from typing import List, Type, TypeVar, Generic

from pydantic import BaseModel, ValidationError

from fukinotou.dataframe_exportable import DataframeExportable
from fukinotou.exception.loading_exception import LoadingException

T = TypeVar("T", bound=BaseModel)


class ParquetRow(BaseModel, Generic[T]):
    """
    Model representing the result of loading a single Parquet row.

    Attributes:
        path: Path to the loaded Parquet file
        value: Single row parsed as a model instance
    """

    path: Path
    value: T


class ParquetLoaded(BaseModel, Generic[T], DataframeExportable):
    """
    Model representing the result of loading an entire Parquet file.

    Attributes:
        path: Path to the loaded Parquet file
        value: List of row load results, each containing a model instance
    """

    path: Path
    value: List[ParquetRow[T]]


class ParquetLoader(Generic[T]):
    """
    Loader for Parquet files that parses rows into the specified Pydantic model.

    This loader uses Polars to read Parquet files and converts each row into
    an instance of the provided Pydantic model. The loader will raise
    exceptions for file not found and invalid paths.
    """

    def __init__(self, model: Type[T]) -> None:
        self.model = model

    def load(self, path: str | Path) -> ParquetLoaded[T]:
        """
        Load and parse the Parquet file into model instances.

        This method reads the Parquet file using Polars, converts each row
        into a Pydantic model instance, and returns a ParquetLoadResult
        containing the file path and a list of row results with model instances.

        Returns:
            ParquetLoaded[T]: Result object containing the file path and list of row results

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If a row fails model validation
        """
        p = Path(path)
        if not p.is_file():
            raise LoadingException(
                original_exception=None, error_message=f"Input path is invalid: {p}"
            )

        # we cannot expect all error of read_parquet()
        try:
            df = pl.read_parquet(p)
        except Exception as e:
            raise LoadingException(
                original_exception=e,
                error_message=f"Error reading Parquet file {p}: {e}",
            )

        results: List[ParquetRow[T]] = []
        for row_dict in df.to_dicts():
            cleaned_dict = {k: v for k, v in row_dict.items() if v is not None}
            try:
                model_instance = self.model.model_validate(cleaned_dict)
            except ValidationError as e:
                raise LoadingException(
                    original_exception=e,
                    error_message=f"Error validating row in {p}: {e}",
                )
            results.append(ParquetRow(path=p, value=model_instance))

        return ParquetLoaded(path=p, value=results)
