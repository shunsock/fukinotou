from pathlib import Path

from typing import Generic, TypeVar, List, Dict, Any, Protocol
from pydantic import BaseModel

import polars
import pandas

V = TypeVar("V", bound=BaseModel)


class Row(Protocol[V]):
    value: V
    path: Path


T = TypeVar("T", bound=Row[Any])


class DataframeExportable(Generic[T]):
    path: Path
    value: List[T]

    def _to_dicts(self, use_path: bool) -> List[Dict[str, Any]]:
        if not use_path:
            return [v.value.model_dump() for v in self.value]
        return [{**v.value.model_dump(), "path": str(v.path)} for v in self.value]

    def to_polars(self, include_path_as_column: bool = False) -> polars.DataFrame:
        """Convert the result to a Polars DataFrame.

        This method converts all model instances in the result to a Polars DataFrame.
        Each v in the DataFrame represents one model instance.

        Args:
            include_path_as_column: If True, adds a 'path' column with the file path
                                    for each v. Default is False.

        Returns:
            Polars DataFrame containing the model data
        """
        if not self.value:
            return polars.DataFrame()

        df = polars.DataFrame(self._to_dicts(include_path_as_column))

        return df

    def to_pandas(self, include_path_as_column: bool = False) -> pandas.DataFrame:
        """Convert the result to a Pandas DataFrame.

        This method converts all model instances in the result to a Pandas DataFrame.
        Each v in the DataFrame represents one model instance.

        Args:
            include_path_as_column: If True, adds a 'path' column with the file path
                                    for each v. Default is False.

        Returns:
            Pandas DataFrame containing the model data
        """
        if not self.value:
            return pandas.DataFrame()

        df = pandas.DataFrame(self._to_dicts(include_path_as_column))

        return df
