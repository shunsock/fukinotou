import os
import tempfile
from pathlib import Path

import pytest

from fukinotou.text_file_loader import TextFileLoader, TextFilesLoader, TextFileLoadResult, TextFilesLoadResult


class TestTextFileLoader:
    def test_init_with_nonexistent_file(self) -> None:
        """
        Test that TextFileLoader initialization raises FileNotFoundError when file doesn't exist.
        
        This test verifies that an appropriate exception is raised when trying to 
        initialize a TextFileLoader with a path that doesn't exist on the file system.
        
        Expected: FileNotFoundError with message containing "File not found"
        """
        # Arrange
        non_existent_path = Path("/path/to/nonexistent/file.txt")
        
        # Act & Assert
        with pytest.raises(FileNotFoundError) as excinfo:
            TextFileLoader(non_existent_path)
        
        assert "File not found" in str(excinfo.value)
    
    def test_init_with_directory_path(self) -> None:
        """
        Test that TextFileLoader initialization raises ValueError when given a directory path.
        
        This test verifies that the loader correctly identifies when a provided path 
        points to a directory rather than a file and raises an appropriate exception.
        
        Expected: ValueError with message containing "Input path is directory path"
        """
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = Path(temp_dir)
            
            # Act & Assert
            with pytest.raises(ValueError) as excinfo:
                TextFileLoader(dir_path)
            
            assert "Input path is directory path" in str(excinfo.value)
    
    def test_load_text_file_successfully(self) -> None:
        """
        Test that TextFileLoader.load() correctly reads and returns the file content.
        
        This test creates a temporary text file with known content, loads it using
        TextFileLoader, and verifies that the result contains the correct file path
        and exact file content.
        
        Expected: TextFileLoadResult instance with matching path and content values
        """
        # Arrange
        expected_content = "Hello, world!\nThis is a test file."
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as temp_file:
            temp_file.write(expected_content)
            temp_path = Path(temp_file.name)
        
        try:
            loader = TextFileLoader(temp_path)
            
            # Act
            result = loader.load()
            
            # Assert
            assert isinstance(result, TextFileLoadResult)
            assert result.path == temp_path
            assert result.value == expected_content
        finally:
            # Clean up
            os.unlink(temp_path)


class TestTextFilesLoader:
    def test_init_with_nonexistent_directory(self) -> None:
        """
        Test that TextFilesLoader initialization raises FileNotFoundError when directory doesn't exist.
        
        This test verifies that an appropriate exception is raised when trying to 
        initialize a TextFilesLoader with a directory path that doesn't exist.
        
        Expected: FileNotFoundError with message containing "File not found"
        """
        # Arrange
        non_existent_dir = Path("/path/to/nonexistent/directory")
        
        # Act & Assert
        with pytest.raises(FileNotFoundError) as excinfo:
            TextFilesLoader(non_existent_dir)
        
        assert "File not found" in str(excinfo.value)
    
    def test_init_with_file_path(self) -> None:
        """
        Test that TextFilesLoader initialization raises ValueError when given a file path.
        
        This test verifies that the loader correctly identifies when a provided path 
        points to a file rather than a directory and raises an appropriate exception.
        
        Expected: ValueError with message containing "Input path is file path"
        """
        # Arrange
        with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
            file_path = Path(temp_file.name)
            
            # Act & Assert
            with pytest.raises(ValueError) as excinfo:
                TextFilesLoader(file_path)
            
            assert "Input path is file path" in str(excinfo.value)
    
    def test_load_multiple_text_files(self) -> None:
        """
        Test that TextFilesLoader.load() correctly loads all text files from a directory.
        
        This test sets up a directory structure with multiple text files in both
        the root and a subdirectory, along with a non-text file that should be ignored.
        It verifies that:
        1. All text files are loaded recursively
        2. Each file's content is read correctly
        3. Non-text files are ignored
        4. The result contains the correct directory path
        
        Expected: 
        - TextFilesLoadResult instance with directory_path matching the input path
        - 5 text files loaded (3 in root, 2 in subdirectory)
        - Each file's content matching what was written
        - PDF file not included in the results
        """
        # Arrange
        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = Path(temp_dir)
            
            # Create test files
            file_contents = {
                "file1.txt": "Content of file 1",
                "file2.txt": "Content of file 2",
                "file3.txt": "Content of file 3",
                "non_text.pdf": "This should be ignored",
            }
            
            file_paths = {}
            for filename, content in file_contents.items():
                file_path = dir_path / filename
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                file_paths[filename] = file_path
            
            # Create a subdirectory with more text files
            subdir_path = dir_path / "subdir"
            subdir_path.mkdir()
            
            subdir_contents = {
                "subfile1.txt": "Subdir content 1",
                "subfile2.txt": "Subdir content 2",
            }
            
            for filename, content in subdir_contents.items():
                file_path = subdir_path / filename
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                file_paths[f"subdir/{filename}"] = file_path
            
            # Act
            loader = TextFilesLoader(dir_path)
            result = loader.load()
            
            # Assert
            assert isinstance(result, TextFilesLoadResult)
            assert result.directory_path == dir_path
            
            # Should find 5 text files (3 in root dir, 2 in subdir)
            assert len(result.value) == 5
            
            # Check that we loaded all text files with correct content
            loaded_files = {result_item.path.name: result_item.value for result_item in result.value}
            
            assert "file1.txt" in loaded_files
            assert loaded_files["file1.txt"] == "Content of file 1"
            
            assert "file2.txt" in loaded_files
            assert loaded_files["file2.txt"] == "Content of file 2"
            
            assert "file3.txt" in loaded_files
            assert loaded_files["file3.txt"] == "Content of file 3"
            
            assert "subfile1.txt" in loaded_files
            assert loaded_files["subfile1.txt"] == "Subdir content 1"
            
            assert "subfile2.txt" in loaded_files
            assert loaded_files["subfile2.txt"] == "Subdir content 2"
            
            # Make sure PDF file was not loaded
            assert "non_text.pdf" not in loaded_files