import csv
from pathlib import Path
from typing import Dict, List, Type, TypeVar, Generic
import polars
import pandas

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class CsvRowLoadResult(BaseModel, Generic[T]):
    """Model representing the result of loading a single CSV row.

    Attributes:
        path: Path to the loaded file
        value: Content of the file as model instance
    """

    path: Path
    value: T


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
            # Return an empty DataFrame if there are no rows
            return polars.DataFrame()

        # Convert each model to a dict
        data_dicts = [row.value.model_dump() for row in self.value]

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
        if not self.value:
            # Return an empty DataFrame if there are no rows
            return pandas.DataFrame()

        # Convert each model to a dict
        data_dicts = [row.value.model_dump() for row in self.value]

        # Create a DataFrame from the list of dicts
        df = pandas.DataFrame(data_dicts)

        # Add path column if requested
        if include_path_as_column:
            df["path"] = str(self.path)

        return df


class CsvLoader(Generic[T]):
    """CSV file loader that reads and converts data to specified model instances.

    Args:
        path: Path to the CSV file to load
        model: Pydantic model class to convert each row into

    Raises:
        FileNotFoundError: The specified path does not exist
        ValueError: If the specified path is a directory
    """

    def __init__(self, path: str | Path, model: Type[T]) -> None:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not p.is_file():
            raise ValueError(f"Input path is directory path: {path}")
        self.file_path = p
        self.model = model

    def load(self, encoding: str = "utf-8") -> CsvLoadResult[T]:
        """Load and parse a CSV file into a list of model instances.

        Treats the first row as headers and later rows as data.
        Each row is converted to a model instance with headers as keys.

        Returns:
            CsvLoadResult containing the file path and list of parsed rows
        """
        with self.file_path.open("r", encoding=encoding) as f:
            csv_rows: List[CsvRowLoadResult[T]] = []
            reader = csv.reader(f)
            try:
                headers = next(reader, [])

                for row_data in reader:
                    row_dict: Dict[str, str] = {}
                    for i, header in enumerate(headers):
                        if i < len(row_data):
                            row_dict[header] = row_data[i]

                    model_instance = self.model(**row_dict)

                    csv_rows.append(
                        CsvRowLoadResult(path=self.file_path, value=model_instance)
                    )
            except StopIteration:
                # Handle an empty file
                pass

            return CsvLoadResult(path=self.file_path, value=csv_rows)
