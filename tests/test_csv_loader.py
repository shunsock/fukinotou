import csv
import os
import tempfile
from pathlib import Path

import pytest
from pydantic import BaseModel, Field

from fukinotou.csv_loader import CsvLoader, CsvLoadResult, CsvRowLoadResult


class _TestModel(BaseModel):
    """Test model for CSV validation."""

    name: str = Field(default="")
    age: int = Field(default=0)
    city: str = Field(default="")


class TestCsvLoader:
    def test_init_with_nonexistent_file(self) -> None:
        """
        Test that CsvLoader initialization raises FileNotFoundError when file doesn't exist.

        This test verifies that an appropriate exception is raised when trying to
        initialize a CsvLoader with a path that doesn't exist on the file system.

        Expected: FileNotFoundError with message containing "File not found"
        """
        # Arrange
        non_existent_path = Path("/path/to/nonexistent/file.csv")

        # Act & Assert
        with pytest.raises(FileNotFoundError) as excinfo:
            CsvLoader(non_existent_path, _TestModel)

        assert "File not found" in str(excinfo.value)

    def test_init_with_directory_path(self) -> None:
        """
        Test that CsvLoader initialization raises ValueError when given a directory path.

        This test verifies that the loader correctly identifies when a provided path
        points to a directory rather than a file and raises an appropriate exception.

        Expected: ValueError with message containing "Input path is directory path"
        """
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = Path(temp_dir)

            # Act & Assert
            with pytest.raises(ValueError) as excinfo:
                CsvLoader(dir_path, _TestModel)

            assert "Input path is directory path" in str(excinfo.value)

    def test_init_with_csv_file(self) -> None:
        """
        Test that CsvLoader initializes properly with a valid CSV file.

        This test verifies that the loader can be initialized with a valid CSV file path.

        Expected: No exceptions raised
        """
        # Arrange
        with tempfile.NamedTemporaryFile(suffix=".csv") as temp_file:
            file_path = Path(temp_file.name)

            # Act & Assert - should not raise an exception
            loader = CsvLoader(file_path, _TestModel)
            assert loader.file_path == file_path
            assert loader.model == _TestModel

    def test_load_csv_file_successfully(self) -> None:
        """
        Test that CsvLoader.load() correctly reads and returns the file content.

        This test creates a temporary CSV file with known content, loads it using
        CsvLoader, and verifies that the result contains the correct file path
        and parsed content as a list of model instances.

        Expected: CsvLoadResult instance with matching path and content values
        """
        # Arrange
        csv_data = [
            ["name", "age", "city"],
            ["Alice", "30", "New York"],
            ["Bob", "25", "Chicago"],
            ["Charlie", "35", "San Francisco"],
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            writer = csv.writer(temp_file)
            for row in csv_data:
                writer.writerow(row)
            temp_path = Path(temp_file.name)

        try:
            loader = CsvLoader(temp_path, _TestModel)

            # Act
            result = loader.load()

            # Assert
            assert isinstance(result, CsvLoadResult)
            assert result.path == temp_path

            # Should have 3 rows (excluding header)
            assert len(result.value) == 3

            # Check each row's data matches expected values
            row1 = result.value[0]
            assert isinstance(row1, CsvRowLoadResult)
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

    def test_load_csv_file_with_first_row_as_data(self) -> None:
        """
        Test that CsvLoader.load() can handle CSV files where the first row is data.

        This test creates a temporary CSV file where each row has data that matches the field names.
        The first row is included as part of the data (not treated as a header).

        Expected: CsvLoadResult instance with correctly parsed values
        """
        # Arrange
        csv_data = [
            [
                "name",
                "age",
                "city",
            ],  # First row contains field names but is treated as data
            ["Alice", "30", "New York"],
            ["Bob", "25", "Chicago"],
            ["Charlie", "35", "San Francisco"],
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            writer = csv.writer(temp_file)
            for row in csv_data:
                writer.writerow(row)
            temp_path = Path(temp_file.name)

        try:
            loader = CsvLoader(temp_path, _TestModel)

            # Act
            result = loader.load()

            # Assert
            assert isinstance(result, CsvLoadResult)
            assert result.path == temp_path

            # Should have 3 rows (excluding header)
            assert len(result.value) == 3

            # Check that the model instances were created correctly
            assert result.value[0].value.name == "Alice"
            assert result.value[0].value.age == 30
            assert result.value[0].value.city == "New York"

            assert result.value[1].value.name == "Bob"
            assert result.value[1].value.age == 25
            assert result.value[1].value.city == "Chicago"

            assert result.value[2].value.name == "Charlie"
            assert result.value[2].value.age == 35
            assert result.value[2].value.city == "San Francisco"
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_load_csv_file_with_missing_fields(self) -> None:
        """
        Test that CsvLoader.load() handles CSV files with missing fields.

        This test verifies that the loader can process CSV files where some rows
        are missing certain fields, using the default values from the model.

        Expected: Row values with defaults for missing fields
        """
        # Arrange
        csv_data = [
            ["name", "age"],  # missing city
            ["Alice", "30"],
            ["Bob", "25"],
            ["Charlie"],  # missing age
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            writer = csv.writer(temp_file)
            for row in csv_data:
                writer.writerow(row)
            temp_path = Path(temp_file.name)

        try:
            loader = CsvLoader(temp_path, _TestModel)

            # Act
            result = loader.load()

            # Assert
            assert len(result.value) == 3

            # Check values with defaults
            assert result.value[0].value.city == ""  # default value
            assert result.value[2].value.age == 0  # default value
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_load_csv_file_with_extra_columns(self) -> None:
        """
        Test loading a CSV with extra columns that aren't in the model.

        This test verifies that the loader correctly maps only the columns that match
        model field names and ignores extra columns.

        Expected: Row values mapped only for the columns that match model fields
        """
        # Arrange
        csv_data = [
            [
                "name",
                "age",
                "city",
                "extra_column1",
                "extra_column2",
            ],  # Header includes extra columns
            ["Alice", "30", "New York", "extra1", "extra2"],
            ["Bob", "25", "Chicago", "extra3", "extra4"],
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            writer = csv.writer(temp_file)
            for row in csv_data:
                writer.writerow(row)
            temp_path = Path(temp_file.name)

        try:
            loader = CsvLoader(temp_path, _TestModel)

            # Act
            result = loader.load()

            # Assert
            assert len(result.value) == 2

            # Check that only the expected fields were mapped
            assert result.value[0].value.name == "Alice"
            assert result.value[0].value.age == 30
            assert result.value[0].value.city == "New York"

            assert result.value[1].value.name == "Bob"
            assert result.value[1].value.age == 25
            assert result.value[1].value.city == "Chicago"
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_load_empty_csv_file(self) -> None:
        """
        Test that CsvLoader.load() handles empty CSV files correctly.

        This test verifies that the loader can process an empty CSV file (with header only)
        and returns an empty list of values.

        Expected: Empty list of values
        """
        # Arrange
        csv_data = [
            ["name", "age", "city"]  # header only
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            writer = csv.writer(temp_file)
            for row in csv_data:
                writer.writerow(row)
            temp_path = Path(temp_file.name)

        try:
            loader = CsvLoader(temp_path, _TestModel)

            # Act
            result = loader.load()

            # Assert
            assert isinstance(result, CsvLoadResult)
            assert result.path == temp_path
            assert len(result.value) == 0  # No data rows
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_load_completely_empty_csv_file(self) -> None:
        """
        Test that CsvLoader.load() handles completely empty CSV files correctly.

        This test verifies that the loader can process a completely empty CSV file
        and returns an empty list of values.

        Expected: Empty list of values
        """
        # Arrange
        csv_data = []  # completely empty

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            writer = csv.writer(temp_file)
            for row in csv_data:
                writer.writerow(row)
            temp_path = Path(temp_file.name)

        try:
            loader = CsvLoader(temp_path, _TestModel)

            # Act
            result = loader.load()

            # Assert
            assert isinstance(result, CsvLoadResult)
            assert result.path == temp_path
            assert len(result.value) == 0  # No data rows
        finally:
            # Clean up
            os.unlink(temp_path)
