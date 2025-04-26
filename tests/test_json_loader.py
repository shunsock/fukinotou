from pathlib import Path

import pytest
from pydantic import BaseModel, Field

from fukinotou.json_loader import (
    JsonLoader,
    JsonsLoader,
    JsonLoadResult,
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

        Expected: LoadingError with message containing "Input path is invalid"
        """
        # Arrange
        non_existent_path = Path(__file__).parent / "json" / "nonexistent.json"
        loader = JsonLoader(_TestModel)

        # Act & Assert
        with pytest.raises(LoadingError, match="Input path is invalid"):
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
        with pytest.raises(ValueError, match="Input path is invalid"):
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
