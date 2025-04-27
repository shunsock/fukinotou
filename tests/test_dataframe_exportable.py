from pathlib import Path
from typing import List

import pytest
import polars
import pandas
from pydantic import BaseModel

from fukinotou.abstraction.dataframe_exportable import DataframeExportable


class _SampleModel(BaseModel):
    id: int
    name: str


class _SampleRow:
    def __init__(self, value: _SampleModel, path: Path):
        self.value = value
        self.path = path


class TestDataframeExportable:
    @pytest.fixture
    def sample_data(self) -> List[_SampleRow]:
        """Create sample test data."""
        return [
            _SampleRow(_SampleModel(id=1, name="Item 1"), Path("/path/to/file1.txt")),
            _SampleRow(_SampleModel(id=2, name="Item 2"), Path("/path/to/file2.txt")),
            _SampleRow(_SampleModel(id=3, name="Item 3"), Path("/path/to/file3.txt")),
        ]

    @pytest.fixture
    def export_obj(self, sample_data) -> DataframeExportable:
        """Create a DataframeExportable instance with sample data."""
        obj = DataframeExportable()
        obj.path = Path("/path/to")
        obj.value = sample_data
        return obj

    def test_to_polars_without_path(self, export_obj):
        """Test conversion to Polars DataFrame without path column."""
        # Act
        df = export_obj.to_polars(include_path_as_column=False)

        # Assert
        assert isinstance(df, polars.DataFrame)
        assert len(df) == 3
        assert "id" in df.columns
        assert "name" in df.columns
        assert "path" not in df.columns

        # Check data
        assert df["id"].to_list() == [1, 2, 3]
        assert df["name"].to_list() == ["Item 1", "Item 2", "Item 3"]

    def test_to_polars_with_path(self, export_obj):
        """Test conversion to Polars DataFrame with path column."""
        # Act
        df = export_obj.to_polars(include_path_as_column=True)

        # Assert
        assert isinstance(df, polars.DataFrame)
        assert len(df) == 3
        assert "id" in df.columns
        assert "name" in df.columns
        assert "path" in df.columns

        # Check data
        assert df["path"].to_list() == [
            "/path/to/file1.txt",
            "/path/to/file2.txt",
            "/path/to/file3.txt",
        ]

    def test_to_pandas_without_path(self, export_obj):
        """Test conversion to Pandas DataFrame without path column."""
        # Act
        df = export_obj.to_pandas(include_path_as_column=False)

        # Assert
        assert isinstance(df, pandas.DataFrame)
        assert len(df) == 3
        assert "id" in df.columns
        assert "name" in df.columns
        assert "path" not in df.columns

        # Check data
        assert df["id"].tolist() == [1, 2, 3]
        assert df["name"].tolist() == ["Item 1", "Item 2", "Item 3"]

    def test_to_pandas_with_path(self, export_obj):
        """Test conversion to Pandas DataFrame with path column."""
        # Act
        df = export_obj.to_pandas(include_path_as_column=True)

        # Assert
        assert isinstance(df, pandas.DataFrame)
        assert len(df) == 3
        assert "id" in df.columns
        assert "name" in df.columns
        assert "path" in df.columns

        # Check data
        assert df["path"].tolist() == [
            "/path/to/file1.txt",
            "/path/to/file2.txt",
            "/path/to/file3.txt",
        ]

    def test_empty_polars_dataframe(self):
        """Test conversion of empty data to Polars DataFrame."""
        # Arrange
        obj = DataframeExportable()
        obj.path = Path("/path/to")
        obj.value = []

        # Act
        df = obj.to_polars()

        # Assert
        assert isinstance(df, polars.DataFrame)
        assert len(df) == 0

    def test_empty_pandas_dataframe(self):
        """Test conversion of empty data to Pandas DataFrame."""
        # Arrange
        obj = DataframeExportable()
        obj.path = Path("/path/to")
        obj.value = []

        # Act
        df = obj.to_pandas()

        # Assert
        assert isinstance(df, pandas.DataFrame)
        assert len(df) == 0
