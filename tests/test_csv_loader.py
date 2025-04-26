import pytest
from pathlib import Path

from pydantic import BaseModel
from fukinotou.csv_loader import CsvLoader, LoadingError


class Person(BaseModel):
    name: str
    age: int


def test_csv_loader_basic():
    """Test basic loading of a CSV file."""
    # Arrange
    loader = CsvLoader(Person)
    test_csv_path = Path(__file__).parent / "example.csv"
    
    # Act
    result = loader.load(test_csv_path)
    
    # Assert
    assert len(result.value) == 2
    assert str(result.path) == str(test_csv_path)
    
    # Check first row
    assert result.value[0].row.name == "John"
    assert result.value[0].row.age == 10
    
    # Check second row
    assert result.value[1].row.name == "Mary"
    assert result.value[1].row.age == 11


def test_csv_loader_to_polars():
    """Test conversion to Polars DataFrame."""
    # Arrange
    loader = CsvLoader(Person)
    test_csv_path = Path(__file__).parent / "example.csv"
    
    # Act
    result = loader.load(test_csv_path)
    df = result.to_polars()
    df_with_path = result.to_polars(include_path_as_column=True)
    
    # Assert
    assert df.shape == (2, 2)
    assert df_with_path.shape == (2, 3)
    
    assert df["name"].to_list() == ["John", "Mary"]
    assert df["age"].to_list() == [10, 11]
    
    assert "path" in df_with_path.columns
    assert all(str(test_csv_path) == path for path in df_with_path["path"].to_list())


def test_csv_loader_to_pandas():
    """Test conversion to Pandas DataFrame."""
    # Arrange
    loader = CsvLoader(Person)
    test_csv_path = Path(__file__).parent / "example.csv"
    
    # Act
    result = loader.load(test_csv_path)
    df = result.to_pandas()
    df_with_path = result.to_pandas(include_path_as_column=True)
    
    # Assert
    assert df.shape == (2, 2)
    assert df_with_path.shape == (2, 3)
    
    assert df["name"].tolist() == ["John", "Mary"]
    assert df["age"].tolist() == [10, 11]
    
    assert "path" in df_with_path.columns
    assert all(str(test_csv_path) == path for path in df_with_path["path"].tolist())


def test_csv_loader_file_not_found():
    """Test loading a non-existent file."""
    # Arrange
    loader = CsvLoader(Person)
    non_existent_path = Path(__file__).parent / "does_not_exist.csv"
    
    # Act & Assert
    with pytest.raises(LoadingError, match="File not found"):
        loader.load(non_existent_path)


def test_csv_loader_empty_file(tmp_path):
    """Test loading an empty CSV file."""
    # Arrange
    loader = CsvLoader(Person)
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("")
    
    # Act & Assert
    with pytest.raises(LoadingError, match="No headers found"):
        loader.load(empty_file)