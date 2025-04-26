from pathlib import Path

import pytest
import polars
import pandas
from pydantic import BaseModel, Field

from fukinotou.json_loader import (
    JsonLoader,
    JsonsLoader,
    JsonLoadResult,
    JsonsLoadResult,
    LoadingError,
)


class _TestModel(BaseModel):
    """Test model for JSON validation."""

    name: str = Field(default="")
    values: list[int] = Field(default_factory=list)
    nested: dict = Field(default_factory=dict)
    id: int = Field(default=0)


class TestJsonLoader:
    def test_load_nonexistent_file(self) -> None:
        """
        Test that JsonLoader.load() raises LoadingError when file doesn't exist.

        This test verifies that an appropriate exception is raised when trying to
        load a JSON file with a path that doesn't exist on the file system.

        Expected: LoadingError with message containing "File not found"
        """
        # Arrange
        non_existent_path = Path(__file__).parent / "json" / "nonexistent.json"
        loader = JsonLoader(_TestModel)

        # Act & Assert
        with pytest.raises(LoadingError, match="File not found"):
            loader.load(non_existent_path)

    def test_load_directory_path(self) -> None:
        """
        Test that JsonLoader.load() raises ValueError when given a directory path.

        This test verifies that the loader correctly identifies when a provided path
        points to a directory rather than a file and raises an appropriate exception.

        Expected: ValueError with message containing "Input path is directory path"
        """
        # Arrange
        dir_path = Path(__file__).parent / "json"
        loader = JsonLoader(_TestModel)

        # Act & Assert
        with pytest.raises(ValueError, match="Input path is directory path"):
            loader.load(dir_path)

    def test_load_json_file_successfully(self) -> None:
        """
        Test that JsonLoader.load() correctly reads and returns the file content.

        This test loads a real JSON file with known content using JsonLoader,
        and verifies that the result contains the correct file path and
        exact file content as a Python dictionary.

        Expected: JsonLoadResult instance with matching path and content values
        """
        # Arrange
        test_file_path = Path(__file__).parent / "json" / "file1.json"
        loader = JsonLoader(_TestModel)

        # Act
        result = loader.load(test_file_path)

        # Assert
        assert isinstance(result, JsonLoadResult)
        assert result.path == test_file_path

        # Check model fields match expected content
        assert result.value.name == "Example 1"
        assert result.value.values == [1, 2, 3]
        assert result.value.nested == {"key": "value1"}
        assert result.value.id == 1

    def test_load_invalid_json_schema(self) -> None:
        """
        Test that JsonLoader.load() raises LoadingError when JSON doesn't match schema.

        This test verifies that the loader correctly detects when JSON content
        doesn't match the expected schema and raises an appropriate exception.

        Expected: LoadingError with message containing "Error validating"
        """
        # Arrange
        invalid_file_path = Path(__file__).parent / "json" / "invalid.json"
        loader = JsonLoader(_TestModel)

        # Act & Assert
        with pytest.raises(LoadingError, match="Error validating"):
            loader.load(invalid_file_path)

    def test_load_broken_json_syntax(self) -> None:
        """
        Test that JsonLoader.load() raises LoadingError when JSON has syntax errors.

        This test verifies that the loader correctly detects when a file contains
        invalid JSON syntax and raises an appropriate exception.

        Expected: LoadingError with message containing "Error parsing JSON file"
        """
        # Arrange
        broken_file_path = Path(__file__).parent / "json" / "broken.json"
        loader = JsonLoader(_TestModel)

        # Act & Assert
        with pytest.raises(LoadingError, match="Error parsing JSON file"):
            loader.load(broken_file_path)


class TestJsonsLoader:
    def test_load_nonexistent_directory(self) -> None:
        """
        Test that JsonsLoader.load() raises LoadingError when directory doesn't exist.

        This test verifies that an appropriate exception is raised when trying to
        load JSON files from a directory path that doesn't exist.

        Expected: LoadingError with message containing "Directory not found"
        """
        # Arrange
        non_existent_dir = Path(__file__).parent / "nonexistent_directory"
        loader = JsonsLoader(_TestModel)

        # Act & Assert
        with pytest.raises(LoadingError, match="Directory not found"):
            loader.load(non_existent_dir)

    def test_load_file_path(self) -> None:
        """
        Test that JsonsLoader.load() raises LoadingError when given a file path.

        This test verifies that the loader correctly identifies when a provided path
        points to a file rather than a directory and raises an appropriate exception.

        Expected: LoadingError with message containing "Input path is not directory"
        """
        # Arrange
        file_path = Path(__file__).parent / "json" / "file1.json"
        loader = JsonsLoader(_TestModel)

        # Act & Assert
        with pytest.raises(LoadingError, match="Input path is not directory"):
            loader.load(file_path)

    def test_load_multiple_json_files(self) -> None:
        """
        Test that JsonsLoader.load() correctly loads all JSON files from a directory.

        This test loads JSON files from a real directory structure with multiple files
        in both the root and a subdirectory, along with a non-JSON file.
        It verifies that:
        1. All JSON files are loaded recursively
        2. Each file's content is parsed correctly
        3. Non-JSON files are ignored
        4. The result contains the correct directory path

        Expected:
        - JsonsLoadResult instance with directory_path matching the input path
        - 5 JSON files loaded (3 in root, 2 in subdirectory)
        - Each file's content matching what's in the actual files
        - XML file not included in the results
        """
        # Arrange
        dir_path = Path(__file__).parent / "json"
        loader = JsonsLoader(_TestModel)

        # Act
        result = loader.load(dir_path)

        # Assert
        assert isinstance(result, JsonsLoadResult)
        assert result.directory_path == dir_path

        # We should find 5 valid JSON files (3 in root dir, 2 in subdir)
        # Note: broken.json and invalid.json will be skipped due to parsing/validation errors
        valid_json_count = 5
        assert len(result.value) == valid_json_count

        # Create a dictionary of loaded files by filename for easier assertions
        loaded_files = {
            result_item.path.name: result_item.value for result_item in result.value
        }

        # Check that we loaded all expected JSON files with correct content
        assert "file1.json" in loaded_files
        assert loaded_files["file1.json"].id == 1
        assert loaded_files["file1.json"].name == "Example 1"

        assert "file2.json" in loaded_files
        assert loaded_files["file2.json"].id == 2
        assert loaded_files["file2.json"].name == "Example 2"

        assert "file3.json" in loaded_files
        assert loaded_files["file3.json"].id == 3
        assert loaded_files["file3.json"].name == "Example 3"

        assert "subfile1.json" in loaded_files
        assert loaded_files["subfile1.json"].id == 4
        assert loaded_files["subfile1.json"].name == "Subdir 1"

        assert "subfile2.json" in loaded_files
        assert loaded_files["subfile2.json"].id == 5
        assert loaded_files["subfile2.json"].name == "Subdir 2"

        # Make sure non-JSON, broken and invalid files were not loaded
        assert "non_json.xml" not in loaded_files
        assert "broken.json" not in loaded_files
        assert "invalid.json" not in loaded_files

    def test_jsons_load_result_to_polars(self) -> None:
        """
        Test that JsonsLoadResult.to_polars() correctly converts model instances to a Polars DataFrame.

        This test loads real JSON files, converts the results to a Polars DataFrame,
        and verifies that the DataFrame has the expected structure and content.

        Expected: Polars DataFrame with rows matching the model instances
        """
        # Arrange
        dir_path = Path(__file__).parent / "json"
        loader = JsonsLoader(_TestModel)

        # Act
        result = loader.load(dir_path)

        # Convert to DataFrames
        df = result.to_polars()
        df_with_path = result.to_polars(include_path_as_column=True)

        # Assert
        assert isinstance(df, polars.DataFrame)
        assert len(df) == 5  # 5 valid JSON files

        # Check column names
        assert "id" in df.columns
        assert "name" in df.columns
        assert "path" not in df.columns

        # Check values
        ids = df.select("id").to_series().to_list()
        assert sorted(ids) == [1, 2, 3, 4, 5]

        # Check with path column
        assert "path" in df_with_path.columns
        assert len(df_with_path.select("path").unique()) == 5  # 5 unique file paths

    def test_jsons_load_result_to_pandas(self) -> None:
        """
        Test that JsonsLoadResult.to_pandas() correctly converts model instances to a Pandas DataFrame.

        This test loads real JSON files, converts the results to a Pandas DataFrame,
        and verifies that the DataFrame has the expected structure and content.

        Expected: Pandas DataFrame with rows matching the model instances
        """
        # Arrange
        dir_path = Path(__file__).parent / "json"
        loader = JsonsLoader(_TestModel)

        # Act
        result = loader.load(dir_path)

        # Convert to DataFrames
        df = result.to_pandas()
        df_with_path = result.to_pandas(include_path_as_column=True)

        # Assert
        assert isinstance(df, pandas.DataFrame)
        assert len(df) == 5  # 5 valid JSON files

        # Check column names
        assert "id" in df.columns
        assert "name" in df.columns
        assert "path" not in df.columns

        # Check values
        ids = df["id"].tolist()
        assert sorted(ids) == [1, 2, 3, 4, 5]

        # Check with path column
        assert "path" in df_with_path.columns
        assert len(df_with_path["path"].unique()) == 5  # 5 unique file paths
