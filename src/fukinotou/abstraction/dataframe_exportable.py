from pathlib import Path

from typing import List, Any


import polars
import pandas


class DataframeExportable:
    path: Path
    value: List[Any]

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

        data_dicts = [row.value.model_dump() for row in self.value]
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

        data_dicts = [row.value.model_dump() for row in self.value]
        df = pandas.DataFrame(data_dicts)

        if include_path_as_column:
            df["path"] = str(self.path)

        return df
