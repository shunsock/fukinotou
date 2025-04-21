import json
import os
import tempfile
from pathlib import Path

import pytest
from pydantic import BaseModel, Field

from fukinotou.json_loader import JsonLoader, JsonsLoader, JsonLoadResult, JsonsLoadResult


class _TestModel(BaseModel):
    """Test model for JSON validation."""
    name: str = Field(default="")
    values: list[int] = Field(default_factory=list)
    nested: dict = Field(default_factory=dict)
    id: int = Field(default=0)


class TestJsonLoader:
    def test_init_with_nonexistent_file(self) -> None:
        """
        Test that JsonLoader initialization raises FileNotFoundError when file doesn't exist.
        
        This test verifies that an appropriate exception is raised when trying to 
        initialize a JsonLoader with a path that doesn't exist on the file system.
        
        Expected: FileNotFoundError with message containing "File not found"
        """
        # Arrange
        non_existent_path = Path("/path/to/nonexistent/file.json")
        
        # Act & Assert
        with pytest.raises(FileNotFoundError) as excinfo:
            JsonLoader(non_existent_path, _TestModel)
        
        assert "File not found" in str(excinfo.value)
    
    def test_init_with_directory_path(self) -> None:
        """
        Test that JsonLoader initialization raises ValueError when given a directory path.
        
        This test verifies that the loader correctly identifies when a provided path 
        points to a directory rather than a file and raises an appropriate exception.
        
        Expected: ValueError with message containing "Input path is directory path"
        """
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = Path(temp_dir)
            
            # Act & Assert
            with pytest.raises(ValueError) as excinfo:
                JsonLoader(dir_path, _TestModel)
            
            assert "Input path is directory path" in str(excinfo.value)
    
    def test_load_json_file_successfully(self) -> None:
        """
        Test that JsonLoader.load() correctly reads and returns the file content.
        
        This test creates a temporary JSON file with known content, loads it using
        JsonLoader, and verifies that the result contains the correct file path
        and exact file content as a Python dictionary.
        
        Expected: JsonLoadResult instance with matching path and content values
        """
        # Arrange
        expected_content = {"name": "test", "values": [1, 2, 3], "nested": {"key": "value"}}
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as temp_file:
            json.dump(expected_content, temp_file)
            temp_path = Path(temp_file.name)
        
        try:
            loader = JsonLoader(temp_path, _TestModel)
            
            # Act
            result = loader.load()
            
            # Assert
            assert isinstance(result, JsonLoadResult)
            assert result.path == temp_path
            
            # Check model fields match expected content
            assert result.value.name == expected_content["name"]
            assert result.value.values == expected_content["values"]
            assert result.value.nested == expected_content["nested"]
        finally:
            # Clean up
            os.unlink(temp_path)


class TestJsonsLoader:
    def test_init_with_nonexistent_directory(self) -> None:
        """
        Test that JsonsLoader initialization raises FileNotFoundError when directory doesn't exist.
        
        This test verifies that an appropriate exception is raised when trying to 
        initialize a JsonsLoader with a directory path that doesn't exist.
        
        Expected: FileNotFoundError with message containing "Directory not found"
        """
        # Arrange
        non_existent_dir = Path("/path/to/nonexistent/directory")
        
        # Act & Assert
        with pytest.raises(FileNotFoundError) as excinfo:
            JsonsLoader(non_existent_dir, _TestModel)
        
        assert "Directory not found" in str(excinfo.value)
    
    def test_init_with_file_path(self) -> None:
        """
        Test that JsonsLoader initialization raises ValueError when given a file path.
        
        This test verifies that the loader correctly identifies when a provided path 
        points to a file rather than a directory and raises an appropriate exception.
        
        Expected: ValueError with message containing "Input path is file path"
        """
        # Arrange
        with tempfile.NamedTemporaryFile(suffix=".json") as temp_file:
            file_path = Path(temp_file.name)
            
            # Act & Assert
            with pytest.raises(ValueError) as excinfo:
                JsonsLoader(file_path, _TestModel)
            
            assert "Input path is file path" in str(excinfo.value)
    
    def test_load_multiple_json_files(self) -> None:
        """
        Test that JsonsLoader.load() correctly loads all JSON files from a directory.
        
        This test sets up a directory structure with multiple JSON files in both
        the root and a subdirectory, along with a non-JSON file that should be ignored.
        It verifies that:
        1. All JSON files are loaded recursively
        2. Each file's content is parsed correctly
        3. Non-JSON files are ignored
        4. The result contains the correct directory path
        
        Expected: 
        - JsonsLoadResult instance with directory_path matching the input path
        - 5 JSON files loaded (3 in root, 2 in subdirectory)
        - Each file's content matching what was written
        - XML file not included in the results
        """
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = Path(temp_dir)
            
            # Create test files
            file_contents = {
                "file1.json": {"id": 1, "name": " 1"},
                "file2.json": {"id": 2, "name": " 2"},
                "file3.json": {"id": 3, "name": " 3"},
                "non_json.xml": "<xml>This should be ignored</xml>",
            }
            
            file_paths = {}
            for filename, content in file_contents.items():
                file_path = dir_path / filename
                with open(file_path, "w", encoding="utf-8") as f:
                    if filename.endswith(".json"):
                        json.dump(content, f)
                    else:
                        f.write(content)
                file_paths[filename] = file_path
            
            # Create a subdirectory with more JSON files
            subdir_path = dir_path / "subdir"
            subdir_path.mkdir()
            
            subdir_contents = {
                "subfile1.json": {"id": 4, "name": "Subdir  1"},
                "subfile2.json": {"id": 5, "name": "Subdir  2"},
            }
            
            for filename, content in subdir_contents.items():
                file_path = subdir_path / filename
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(content, f)
                file_paths[f"subdir/{filename}"] = file_path
            
            # Act
            loader = JsonsLoader(dir_path, _TestModel)
            result = loader.load()
            
            # Assert
            assert isinstance(result, JsonsLoadResult)
            assert result.directory_path == dir_path
            
            # Should find 5 JSON files (3 in root dir, 2 in subdir)
            assert len(result.value) == 5
            
            # Check that we loaded all JSON files with correct content
            loaded_files = {result_item.path.name: result_item.value for result_item in result.value}
            
            assert "file1.json" in loaded_files
            assert loaded_files["file1.json"].id == 1
            assert loaded_files["file1.json"].name == " 1"
            
            assert "file2.json" in loaded_files
            assert loaded_files["file2.json"].id == 2
            assert loaded_files["file2.json"].name == " 2"
            
            assert "file3.json" in loaded_files
            assert loaded_files["file3.json"].id == 3
            assert loaded_files["file3.json"].name == " 3"
            
            assert "subfile1.json" in loaded_files
            assert loaded_files["subfile1.json"].id == 4
            assert loaded_files["subfile1.json"].name == "Subdir  1"
            
            assert "subfile2.json" in loaded_files
            assert loaded_files["subfile2.json"].id == 5
            assert loaded_files["subfile2.json"].name == "Subdir  2"
            
            # Make sure XML file was not loaded
            assert "non_json.xml" not in loaded_files