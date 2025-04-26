import os
from pathlib import Path
import tempfile
import shutil

import pytest

from fukinotou.path_handler.path_searcher import PathSearcher


class TestPathSearcher:
    @pytest.fixture
    def test_dir(self):
        """Create a temporary directory with various test files."""
        temp_dir = tempfile.mkdtemp()
        try:
            # Create some test files
            with open(os.path.join(temp_dir, "file1.txt"), "w") as f:
                f.write("Test file 1")
            with open(os.path.join(temp_dir, "file2.jpg"), "w") as f:
                f.write("Test file 2")
            with open(os.path.join(temp_dir, "file3.jpg"), "w") as f:
                f.write("Test file 3")
            with open(os.path.join(temp_dir, "file4.png"), "w") as f:
                f.write("Test file 4")
            
            # Create a subdirectory with more files
            os.mkdir(os.path.join(temp_dir, "subdir"))
            with open(os.path.join(temp_dir, "subdir", "file5.txt"), "w") as f:
                f.write("Test file 5")
            with open(os.path.join(temp_dir, "subdir", "file6.jpg"), "w") as f:
                f.write("Test file 6")
            
            yield Path(temp_dir)
        finally:
            shutil.rmtree(temp_dir)
    
    def test_search_file_paths_from_directory_path_with_dir(self, test_dir):
        """Test searching for files in a directory."""
        # Arrange & Act
        files = PathSearcher.search_file_paths_from_directory_path(test_dir)
        
        # Assert
        assert len(files) == 4  # Should find the 4 files in the root directory
        file_names = [f.name for f in files]
        assert "file1.txt" in file_names
        assert "file2.jpg" in file_names
        assert "file3.jpg" in file_names
        assert "file4.png" in file_names
        # Should not find files in subdirectories
        for f in files:
            assert "subdir" not in str(f)
    
    def test_search_file_paths_from_directory_path_with_file(self, test_dir):
        """Test searching with a file path instead of a directory."""
        # Arrange
        file_path = test_dir / "file1.txt"
        
        # Act
        files = PathSearcher.search_file_paths_from_directory_path(file_path)
        
        # Assert
        assert len(files) == 1
        assert files[0] == file_path
    
    def test_search_file_paths_from_directory_path_nonexistent(self):
        """Test searching in a nonexistent directory."""
        # Arrange
        non_existent_path = Path("/nonexistent/directory")
        
        # Act
        files = PathSearcher.search_file_paths_from_directory_path(non_existent_path)
        
        # Assert
        assert files == []
    
    def test_search_specific_extension_paths_from_directory_path(self, test_dir):
        """Test searching for files with a specific extension."""
        # Arrange & Act
        jpg_files = PathSearcher.search_specific_extension_paths_from_directory_path(
            test_dir, ".jpg"
        )
        
        # Assert
        assert len(jpg_files) == 2
        file_names = [f.name for f in jpg_files]
        assert "file2.jpg" in file_names
        assert "file3.jpg" in file_names
        assert "file1.txt" not in file_names
        assert "file4.png" not in file_names
    
    def test_search_specific_extension_paths_without_dot(self, test_dir):
        """Test searching with extension without leading dot."""
        # Arrange & Act
        jpg_files = PathSearcher.search_specific_extension_paths_from_directory_path(
            test_dir, "jpg"
        )
        
        # Assert
        assert len(jpg_files) == 2
        file_names = [f.name for f in jpg_files]
        assert "file2.jpg" in file_names
        assert "file3.jpg" in file_names
    
    def test_search_specific_extension_paths_case_insensitive(self, test_dir):
        """Test that extension search is case-insensitive."""
        # Arrange & Act
        jpg_files = PathSearcher.search_specific_extension_paths_from_directory_path(
            test_dir, ".JPG"
        )
        
        # Assert
        assert len(jpg_files) == 2
        file_names = [f.name for f in jpg_files]
        assert "file2.jpg" in file_names
        assert "file3.jpg" in file_names
    
    def test_search_specific_extensions_paths_from_directory_path(self, test_dir):
        """Test searching for files with multiple extensions."""
        # Arrange & Act
        files = PathSearcher.search_specific_extensions_paths_from_directory_path(
            test_dir, [".txt", ".png"]
        )
        
        # Assert
        assert len(files) == 2
        file_names = [f.name for f in files]
        assert "file1.txt" in file_names
        assert "file4.png" in file_names
        assert "file2.jpg" not in file_names
        assert "file3.jpg" not in file_names
    
    def test_search_specific_extensions_paths_mixed_format(self, test_dir):
        """Test searching with extensions in mixed format (with/without dots)."""
        # Arrange & Act
        files = PathSearcher.search_specific_extensions_paths_from_directory_path(
            test_dir, ["txt", ".png"]
        )
        
        # Assert
        assert len(files) == 2
        file_names = [f.name for f in files]
        assert "file1.txt" in file_names
        assert "file4.png" in file_names
    
    def test_search_specific_extensions_paths_case_insensitive(self, test_dir):
        """Test that multiple extension search is case-insensitive."""
        # Arrange & Act
        files = PathSearcher.search_specific_extensions_paths_from_directory_path(
            test_dir, [".TXT", ".PNG"]
        )
        
        # Assert
        assert len(files) == 2
        file_names = [f.name for f in files]
        assert "file1.txt" in file_names
        assert "file4.png" in file_names