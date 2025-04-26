import os
import tempfile
from pathlib import Path

import pytest
import polars as pl
from pydantic import BaseModel, Field

from fukinotou.parquet_loader import (
    ParquetLoader,
    ParquetLoadResult,
    ParquetRowLoadResult,
    LoadingError,
)


class _TestModel(BaseModel):
    """Test model for Parquet validation."""

    name: str = Field(default="")
    age: int = Field(default=0)
    city: str = Field(default="")


class TestParquetLoader:
    def test_load_nonexistent_file(self) -> None:
        """
        Test that ParquetLoader.load() raises LoadingError when file doesn't exist.

        This test verifies that an appropriate exception is raised when trying to
        load a Parquet file with a path that doesn't exist on the file system.

        Expected: LoadingError with message containing "File not found"
        """
        # Arrange
        non_existent_path = Path("/path/to/nonexistent/file.parquet")
        loader = ParquetLoader(_TestModel)

        # Act & Assert
        with pytest.raises(LoadingError, match="File not found"):
            loader.load(non_existent_path)

    def test_load_directory_path(self) -> None:
        """
        Test that ParquetLoader.load() raises LoadingError when given a directory path.

        This test verifies that the loader correctly identifies when a provided path
        points to a directory rather than a file and raises an appropriate exception.

        Expected: LoadingError with message containing "Input path is a directory"
        """
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = Path(temp_dir)
            loader = ParquetLoader(_TestModel)

            # Act & Assert
            with pytest.raises(LoadingError, match="Input path is a directory"):
                loader.load(dir_path)

    def test_load_parquet_file_successfully(self) -> None:
        """
        Test that ParquetLoader.load() correctly reads and returns the file content.

        This test creates a temporary Parquet file with known content, loads it using
        ParquetLoader, and verifies that the result contains the correct file path
        and parsed content as a list of model instances.

        Expected: ParquetLoadResult instance with matching path and content values
        """
        # Arrange
        data = {
            "name": ["Alice", "Bob", "Charlie"],
            "age": [30, 25, 35],
            "city": ["New York", "Chicago", "San Francisco"],
        }

        df = pl.DataFrame(data)

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        # Write to the temp file
        df.write_parquet(temp_path)

        try:
            loader = ParquetLoader(_TestModel)

            # Act
            result = loader.load(temp_path)

            # Assert
            assert isinstance(result, ParquetLoadResult)
            assert result.path == temp_path

            # Should have 3 rows
            assert len(result.value) == 3

            # Check each row's data matches expected values
            row1 = result.value[0]
            assert isinstance(row1, ParquetRowLoadResult)
            assert row1.path == temp_path
            assert row1.value.name == "Alice"
            assert row1.value.age == 30
            assert row1.value.city == "New York"

            row2 = result.value[1]
            assert row2.value.name == "Bob"
            assert row2.value.age == 25
            assert row2.value.city == "Chicago"

            row3 = result.value[2]
            assert row3.value.name == "Charlie"
            assert row3.value.age == 35
            assert row3.value.city == "San Francisco"
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_load_parquet_file_with_missing_fields(self) -> None:
        """
        Test that ParquetLoader.load() handles Parquet files with missing fields.

        This test verifies that the loader can process Parquet files where some columns
        are missing entirely, using the default values from the model.

        Expected: Row values with defaults for missing fields
        """
        # Arrange
        data = {
            "name": ["Alice", "Bob", "Charlie"],
            "age": [30, 25, 35],
            # Missing city column entirely
        }

        df = pl.DataFrame(data)

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        # Write to the temp file
        df.write_parquet(temp_path)

        try:
            loader = ParquetLoader(_TestModel)

            # Act
            result = loader.load(temp_path)

            # Assert
            assert len(result.value) == 3

            # Check values with defaults for missing column
            for row in result.value:
                assert row.value.city == ""  # default value for missing column
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_load_parquet_file_with_extra_columns(self) -> None:
        """
        Test loading a Parquet file with extra columns that aren't in the model.

        This test verifies that the loader correctly maps only the columns that match
        model field names and ignores extra columns.

        Expected: Row values mapped only for the columns that match model fields
        """
        # Arrange
        data = {
            "name": ["Alice", "Bob"],
            "age": [30, 25],
            "city": ["New York", "Chicago"],
            "extra_column1": ["extra1", "extra3"],
            "extra_column2": ["extra2", "extra4"],
        }

        df = pl.DataFrame(data)

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        # Write to the temp file
        df.write_parquet(temp_path)

        try:
            loader = ParquetLoader(_TestModel)

            # Act
            result = loader.load(temp_path)

            # Assert
            assert len(result.value) == 2

            # Check that only the expected fields were mapped
            assert result.value[0].value.name == "Alice"
            assert result.value[0].value.age == 30
            assert result.value[0].value.city == "New York"

            assert result.value[1].value.name == "Bob"
            assert result.value[1].value.age == 25
            assert result.value[1].value.city == "Chicago"

            # Ensure the model doesn't have the extra columns
            assert not hasattr(result.value[0].value, "extra_column1")
            assert not hasattr(result.value[0].value, "extra_column2")
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_load_parquet_file_with_null_values(self) -> None:
        """
        Test that ParquetLoader.load() handles Parquet files with null values.

        This test verifies that the loader can process Parquet files where some values
        are null/None, using the default values from the model for those fields.

        Expected: Null values replaced with model defaults
        """
        # Arrange
        data = {
            "name": ["Alice", "Bob", None],  # None for name of third row
            "age": [30, None, 35],  # None for age of second row
            "city": ["New York", "Chicago", "San Francisco"],
        }

        df = pl.DataFrame(data)

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        # Write to the temp file
        df.write_parquet(temp_path)

        try:
            loader = ParquetLoader(_TestModel)

            # Act
            result = loader.load(temp_path)

            # Assert
            assert len(result.value) == 3

            # Check null values were replaced with defaults
            assert result.value[1].value.age == 0  # default value for None
            assert result.value[2].value.name == ""  # default value for None
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_load_empty_parquet_file(self) -> None:
        """
        Test that ParquetLoader.load() handles empty Parquet files correctly.

        This test verifies that the loader can process an empty Parquet file
        and returns an empty list of values.

        Expected: Empty list of values
        """
        # Arrange
        data = {"name": [], "age": [], "city": []}

        df = pl.DataFrame(data)

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        # Write to the temp file
        df.write_parquet(temp_path)

        try:
            loader = ParquetLoader(_TestModel)

            # Act
            result = loader.load(temp_path)

            # Assert
            assert isinstance(result, ParquetLoadResult)
            assert result.path == temp_path
            assert len(result.value) == 0  # No data rows
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_to_polars_with_data(self) -> None:
        """
        Test that ParquetLoadResult.to_polars() correctly converts data to Polars DataFrame.

        This test verifies that the to_polars method properly converts the model instances
        to a Polars DataFrame with the expected structure and values.

        Expected: Polars DataFrame with correct data
        """
        # Arrange
        data = {
            "name": ["Alice", "Bob"],
            "age": [30, 25],
            "city": ["New York", "Chicago"],
        }

        df = pl.DataFrame(data)

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        # Write to the temp file
        df.write_parquet(temp_path)

        try:
            loader = ParquetLoader(_TestModel)
            result = loader.load(temp_path)

            # Act
            df = result.to_polars()

            # Assert
            assert df.shape == (2, 3)  # 2 rows, 3 columns (name, age, city)
            assert set(df.columns) == {"name", "age", "city"}
            assert df["name"].to_list() == ["Alice", "Bob"]
            assert df["age"].to_list() == [30, 25]
            assert df["city"].to_list() == ["New York", "Chicago"]

            # Act with path column
            df_with_path = result.to_polars(include_path_as_column=True)

            # Assert
            assert df_with_path.shape == (2, 4)  # 2 rows, 4 columns (with path)
            assert "path" in df_with_path.columns
            assert df_with_path["path"].to_list() == [str(temp_path), str(temp_path)]
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_to_polars_empty_data(self) -> None:
        """
        Test that ParquetLoadResult.to_polars() handles empty data correctly.

        This test verifies that the to_polars method returns an empty
        DataFrame when there are no values in the result.

        Expected: Empty Polars DataFrame
        """
        # Arrange
        data = {"name": [], "age": [], "city": []}
        df = pl.DataFrame(data)

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        # Write to the temp file
        df.write_parquet(temp_path)

        try:
            loader = ParquetLoader(_TestModel)
            result = loader.load(temp_path)

            # Act
            df = result.to_polars()

            # Assert
            assert df.shape == (0, 0)  # Empty DataFrame
            assert len(df.columns) == 0
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_to_pandas_with_data(self) -> None:
        """
        Test that ParquetLoadResult.to_pandas() correctly converts data to Pandas DataFrame.

        This test verifies that the to_pandas method properly converts the model instances
        to a Pandas DataFrame with the expected structure and values.

        Expected: Pandas DataFrame with correct data
        """
        # Arrange
        data = {
            "name": ["Alice", "Bob"],
            "age": [30, 25],
            "city": ["New York", "Chicago"],
        }

        df = pl.DataFrame(data)

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        # Write to the temp file
        df.write_parquet(temp_path)

        try:
            loader = ParquetLoader(_TestModel)
            result = loader.load(temp_path)

            # Act
            df = result.to_pandas()

            # Assert
            assert df.shape == (2, 3)  # 2 rows, 3 columns (name, age, city)
            assert set(df.columns) == {"name", "age", "city"}
            assert df["name"].tolist() == ["Alice", "Bob"]
            assert df["age"].tolist() == [30, 25]
            assert df["city"].tolist() == ["New York", "Chicago"]

            # Act with path column
            df_with_path = result.to_pandas(include_path_as_column=True)

            # Assert
            assert df_with_path.shape == (2, 4)  # 2 rows, 4 columns (with path)
            assert "path" in df_with_path.columns
            assert df_with_path["path"].tolist() == [str(temp_path), str(temp_path)]
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_to_pandas_empty_data(self) -> None:
        """
        Test that ParquetLoadResult.to_pandas() handles empty data correctly.

        This test verifies that the to_pandas method returns an empty
        DataFrame when there are no values in the result.

        Expected: Empty Pandas DataFrame
        """
        # Arrange
        data = {"name": [], "age": [], "city": []}
        df = pl.DataFrame(data)

        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as temp_file:
            temp_path = Path(temp_file.name)

        # Write to the temp file
        df.write_parquet(temp_path)

        try:
            loader = ParquetLoader(_TestModel)
            result = loader.load(temp_path)

            # Act
            df = result.to_pandas()

            # Assert
            assert df.shape == (0, 0)  # Empty DataFrame
            assert len(df.columns) == 0
        finally:
            # Clean up
            os.unlink(temp_path)
