import os
from pathlib import Path

import pytest
from PIL import Image

from fukinotou.image_loader import ImageFileLoader, ImageFilesLoader
from fukinotou.load_error import LoadingError


def test_image_file_loader():
    """Test loading a single image file."""
    test_file = Path(os.path.dirname(os.path.abspath(__file__))) / "example.jpg"

    result = ImageFileLoader.load(path=test_file)

    assert result.path == test_file
    assert isinstance(result.value, Image.Image)
    assert result.value.format == "JPEG"


def test_image_file_loader_not_found():
    """Test error when file does not exist."""
    with pytest.raises(LoadingError):
        ImageFileLoader.load(path="nonexistent.jpg")


def test_image_file_loader_is_directory():
    """Test error when path is a directory."""
    dir_path = Path(os.path.dirname(os.path.abspath(__file__)))
    with pytest.raises(LoadingError):
        ImageFileLoader.load(path=dir_path)


def test_image_files_loader():
    """Test loading multiple image files from directory."""
    dir_path = Path(os.path.dirname(os.path.abspath(__file__)))

    result = ImageFilesLoader.load(path=dir_path, extensions=[".jpg"])

    assert result.directory_path == dir_path
    assert len(result.value) >= 1  # At least our example.jpg should be found

    # Check the first loaded file is our example.jpg
    example_file = next((r for r in result.value if r.path.name == "example.jpg"), None)
    assert example_file is not None
    assert isinstance(example_file.value, Image.Image)
    assert example_file.value.format == "JPEG"


def test_image_files_loader_not_found():
    """Test error when directory does not exist."""
    with pytest.raises(LoadingError):
        ImageFilesLoader.load(path=Path("nonexistent_dir"), extensions=[".jpg"])


def test_image_files_loader_is_file():
    """Test error when path is a file."""
    test_file = Path(os.path.dirname(os.path.abspath(__file__))) / "example.jpg"
    with pytest.raises(LoadingError):
        ImageFilesLoader.load(path=test_file, extensions=[".jpg"])