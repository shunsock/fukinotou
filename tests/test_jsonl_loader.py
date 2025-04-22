import json
import os
import tempfile
from pathlib import Path

import pytest
from pydantic import BaseModel, Field

from fukinotou.jsonl_loader import JsonlLoader, JsonlLoadResult


class _TestModel(BaseModel):
    """Test model for JSONL validation."""

    name: str = Field(default="")
    value: int = Field(default=0)
    tags: list[str] = Field(default_factory=list)


class TestJsonlLoader:
    def test_init_with_nonexistent_file(self) -> None:
        """
        Test that JsonlLoader initialization raises FileNotFoundError when file doesn't exist.

        This test verifies that an appropriate exception is raised when trying to
        initialize a JsonlLoader with a path that doesn't exist on the file system.

        Expected: FileNotFoundError with message containing "File not found"
        """
        # Arrange
        non_existent_path = Path("/path/to/nonexistent/file.jsonl")

        # Act & Assert
        with pytest.raises(FileNotFoundError) as excinfo:
            JsonlLoader(non_existent_path, _TestModel)

        assert "File not found" in str(excinfo.value)

    def test_init_with_directory_path(self) -> None:
        """
        Test that JsonlLoader initialization raises ValueError when given a directory path.

        This test verifies that the loader correctly identifies when a provided path
        points to a directory rather than a file and raises an appropriate exception.

        Expected: ValueError with message containing "Input path is a directory"
        """
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = Path(temp_dir)

            # Act & Assert
            with pytest.raises(ValueError) as excinfo:
                JsonlLoader(dir_path, _TestModel)

            assert "Input path is a directory" in str(excinfo.value)

    def test_load_jsonl_file_successfully(self) -> None:
        """
        Test that JsonlLoader.load() correctly reads and returns the file content.

        This test creates a temporary JSONL file with known content, loads it using
        JsonlLoader, and verifies that the result contains the correct file path
        and parsed content as a list of model instances.

        Expected: JsonlLoadResult instance with matching path and content values
        """
        # Arrange
        jsonl_data = [
            {"name": "Alice", "value": 10, "tags": ["a", "b"]},
            {"name": "Bob", "value": 20, "tags": ["c", "d"]},
            {"name": "Charlie", "value": 30, "tags": ["e", "f"]},
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False
        ) as temp_file:
            for item in jsonl_data:
                temp_file.write(json.dumps(item) + "\n")
            temp_path = Path(temp_file.name)

        try:
            loader = JsonlLoader(temp_path, _TestModel)

            # Act
            result = loader.load()

            # Assert
            assert isinstance(result, JsonlLoadResult)
            assert result.path == temp_path

            # Should have 3 items
            assert len(result.values) == 3

            # Check each item's data matches expected values
            assert result.values[0].name == "Alice"
            assert result.values[0].value == 10
            assert result.values[0].tags == ["a", "b"]

            assert result.values[1].name == "Bob"
            assert result.values[1].value == 20
            assert result.values[1].tags == ["c", "d"]

            assert result.values[2].name == "Charlie"
            assert result.values[2].value == 30
            assert result.values[2].tags == ["e", "f"]
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_load_jsonl_file_with_empty_lines(self) -> None:
        """
        Test that JsonlLoader.load() correctly handles JSONL files with empty lines.

        This test verifies that the loader properly skips empty lines in the file
        and processes only valid JSON lines.

        Expected: JsonlLoadResult instance with only non-empty lines parsed
        """
        # Arrange
        content = """
{"name": "Alice", "value": 10, "tags": ["a", "b"]}

{"name": "Bob", "value": 20, "tags": ["c", "d"]}

{"name": "Charlie", "value": 30, "tags": ["e", "f"]}
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False
        ) as temp_file:
            temp_file.write(content)
            temp_path = Path(temp_file.name)

        try:
            loader = JsonlLoader(temp_path, _TestModel)

            # Act
            result = loader.load()

            # Assert
            assert isinstance(result, JsonlLoadResult)
            assert len(result.values) == 3  # Should still have 3 valid items

            # Check content is correct
            assert result.values[0].name == "Alice"
            assert result.values[1].name == "Bob"
            assert result.values[2].name == "Charlie"
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_load_jsonl_file_with_invalid_json(self) -> None:
        """
        Test that JsonlLoader.load() raises ValueError when encountering invalid JSON.

        This test verifies that the loader properly reports errors when a line
        contains invalid JSON syntax.

        Expected: ValueError with message containing line number information
        """
        # Arrange
        content = """
{"name": "Alice", "value": 10, "tags": ["a", "b"]}
{"name": "Invalid, "value": 20, "tags": ["c", "d"]}
{"name": "Charlie", "value": 30, "tags": ["e", "f"]}
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False
        ) as temp_file:
            temp_file.write(content)
            temp_path = Path(temp_file.name)

        try:
            loader = JsonlLoader(temp_path, _TestModel)

            # Act & Assert
            with pytest.raises(ValueError) as excinfo:
                loader.load()

            # Check that error message contains line number and Invalid JSON
            assert "line" in str(excinfo.value)
            assert "Invalid JSON" in str(excinfo.value)
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_load_empty_jsonl_file(self) -> None:
        """
        Test that JsonlLoader.load() handles empty JSONL files correctly.

        This test verifies that the loader can process an empty JSONL file
        and returns an empty list of values.

        Expected: Empty list of values
        """
        # Arrange
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False
        ) as temp_file:
            temp_path = Path(temp_file.name)

        try:
            loader = JsonlLoader(temp_path, _TestModel)

            # Act
            result = loader.load()

            # Assert
            assert isinstance(result, JsonlLoadResult)
            assert result.path == temp_path
            assert len(result.values) == 0  # No items
        finally:
            # Clean up
            os.unlink(temp_path)

    def test_to_polars_with_data(self) -> None:
        """
        Test that JsonlLoadResult.to_polars() correctly converts data to Polars DataFrame.

        This test verifies that the to_polars method properly converts the model instances
        to a Polars DataFrame with the expected structure and values.

        Expected: Polars DataFrame with correct data
        """
        # Arrange
        jsonl_data = [
            {"name": "Alice", "value": 10, "tags": ["a", "b"]},
            {"name": "Bob", "value": 20, "tags": ["c", "d"]},
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False
        ) as temp_file:
            for item in jsonl_data:
                temp_file.write(json.dumps(item) + "\n")
            temp_path = Path(temp_file.name)

        try:
            loader = JsonlLoader(temp_path, _TestModel)
            result = loader.load()

            # Act
            df = result.to_polars()

            # Assert
            assert df.shape == (2, 3)  # 2 rows, 3 columns (name, value, tags)
            assert df.columns == ["name", "value", "tags"]
            assert df["name"].to_list() == ["Alice", "Bob"]
            assert df["value"].to_list() == [10, 20]
            assert df["tags"].to_list() == [["a", "b"], ["c", "d"]]

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
        Test that JsonlLoadResult.to_polars() handles empty data correctly.

        This test verifies that the to_polars method returns an empty
        DataFrame when there are no values in the result.

        Expected: Empty Polars DataFrame
        """
        # Arrange
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False
        ) as temp_file:
            temp_path = Path(temp_file.name)

        try:
            loader = JsonlLoader(temp_path, _TestModel)
            result = loader.load()

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
        Test that JsonlLoadResult.to_pandas() correctly converts data to Pandas DataFrame.

        This test verifies that the to_pandas method properly converts the model instances
        to a Pandas DataFrame with the expected structure and values.

        Expected: Pandas DataFrame with correct data
        """
        # Arrange
        jsonl_data = [
            {"name": "Alice", "value": 10, "tags": ["a", "b"]},
            {"name": "Bob", "value": 20, "tags": ["c", "d"]},
        ]

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False
        ) as temp_file:
            for item in jsonl_data:
                temp_file.write(json.dumps(item) + "\n")
            temp_path = Path(temp_file.name)

        try:
            loader = JsonlLoader(temp_path, _TestModel)
            result = loader.load()

            # Act
            df = result.to_pandas()

            # Assert
            assert df.shape == (2, 3)  # 2 rows, 3 columns (name, value, tags)
            assert list(df.columns) == ["name", "value", "tags"]
            assert df["name"].tolist() == ["Alice", "Bob"]
            assert df["value"].tolist() == [10, 20]
            assert df["tags"].tolist() == [["a", "b"], ["c", "d"]]

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
        Test that JsonlLoadResult.to_pandas() handles empty data correctly.

        This test verifies that the to_pandas method returns an empty
        DataFrame when there are no values in the result.

        Expected: Empty Pandas DataFrame
        """
        # Arrange
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".jsonl", delete=False
        ) as temp_file:
            temp_path = Path(temp_file.name)

        try:
            loader = JsonlLoader(temp_path, _TestModel)
            result = loader.load()

            # Act
            df = result.to_pandas()

            # Assert
            assert df.shape == (0, 0)  # Empty DataFrame
            assert len(df.columns) == 0
        finally:
            # Clean up
            os.unlink(temp_path)
