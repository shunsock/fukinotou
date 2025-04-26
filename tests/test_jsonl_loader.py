import pytest
from pathlib import Path

from pydantic import BaseModel
from fukinotou.jsonl_loader import JsonlLoader, LoadingError


class Person(BaseModel):
    """Test model for JSONL data."""

    name: str
    age: int
    city: str = "Unknown"


def test_jsonl_loader_basic() -> None:
    """Test basic loading of a JSONL file."""
    # Arrange
    loader = JsonlLoader(Person)
    test_file_path = Path(__file__).parent / "jsonl/example.jsonl"

    # Act
    result = loader.load(test_file_path)

    # Assert
    assert len(result.value) == 3
    assert str(result.path) == str(test_file_path)

    # Check first row
    assert result.value[0].row.name == "John"
    assert result.value[0].row.age == 30
    assert result.value[0].row.city == "New York"

    # Check third row (with default value)
    assert result.value[2].row.name == "Bob"
    assert result.value[2].row.age == 40
    assert result.value[2].row.city == "Unknown"  # Default value


def test_jsonl_loader_to_polars() -> None:
    """Test conversion to Polars DataFrame."""
    # Arrange
    loader = JsonlLoader(Person)
    test_file_path = Path(__file__).parent / "jsonl/example.jsonl"

    # Act
    result = loader.load(test_file_path)
    df = result.to_polars()
    df_with_path = result.to_polars(include_path_as_column=True)

    # Assert
    assert df.shape == (3, 3)  # 3 rows, 3 columns (name, age, city)
    assert df_with_path.shape == (3, 4)  # 3 rows, 4 columns (name, age, city, path)

    assert df["name"].to_list() == ["John", "Alice", "Bob"]
    assert df["age"].to_list() == [30, 25, 40]
    assert df["city"].to_list() == ["New York", "Boston", "Unknown"]

    assert "path" in df_with_path.columns
    assert all(str(test_file_path) == path for path in df_with_path["path"].to_list())


def test_jsonl_loader_to_pandas() -> None:
    """Test conversion to Pandas DataFrame."""
    # Arrange
    loader = JsonlLoader(Person)
    test_file_path = Path(__file__).parent / "jsonl/example.jsonl"

    # Act
    result = loader.load(test_file_path)
    df = result.to_pandas()
    df_with_path = result.to_pandas(include_path_as_column=True)

    # Assert
    assert df.shape == (3, 3)  # 3 rows, 3 columns (name, age, city)
    assert df_with_path.shape == (3, 4)  # 3 rows, 4 columns (name, age, city, path)

    assert df["name"].tolist() == ["John", "Alice", "Bob"]
    assert df["age"].tolist() == [30, 25, 40]
    assert df["city"].tolist() == ["New York", "Boston", "Unknown"]

    assert "path" in df_with_path.columns
    assert all(str(test_file_path) == path for path in df_with_path["path"].tolist())


def test_jsonl_loader_file_not_found() -> None:
    """Test loading a non-existent file."""
    # Arrange
    loader = JsonlLoader(Person)
    non_existent_path = Path(__file__).parent / "jsonl/does_not_exist.jsonl"

    # Act & Assert
    with pytest.raises(LoadingError, match="File not found"):
        loader.load(non_existent_path)


def test_jsonl_loader_empty_file() -> None:
    """Test loading an empty JSONL file."""
    # Arrange
    loader = JsonlLoader(Person)
    empty_file_path = Path(__file__).parent / "jsonl/empty.jsonl"

    # Act
    result = loader.load(empty_file_path)

    # Assert
    assert len(result.value) == 0
    assert str(result.path) == str(empty_file_path)


def test_jsonl_loader_invalid_json() -> None:
    """Test loading a JSONL file with invalid JSON."""
    # Arrange
    loader = JsonlLoader(Person)
    invalid_json_path = Path(__file__).parent / "jsonl/invalid_json.jsonl"

    # Act & Assert
    with pytest.raises(LoadingError, match="Error parsing JSON on line 2"):
        loader.load(invalid_json_path)


def test_jsonl_loader_invalid_schema() -> None:
    """Test loading a JSONL file with data that doesn't match the schema."""
    # Arrange
    loader = JsonlLoader(Person)
    invalid_schema_path = Path(__file__).parent / "jsonl/invalid_schema.jsonl"

    # Act & Assert
    with pytest.raises(LoadingError, match="Error validating row 1"):
        loader.load(invalid_schema_path)
