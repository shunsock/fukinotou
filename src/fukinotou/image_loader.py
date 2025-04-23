from pathlib import Path
from typing import List

from pydantic import BaseModel, ConfigDict
from PIL import Image

from .path_handler.path_searcher import PathSearcher


class ImageFileLoadResult(BaseModel):
    """
    Model representing the result of loading a image file.

    Attributes:
        path: Path to the loaded file
        value: Content of the file
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    path: Path
    value: Image.Image


class ImageFileLoader:
    """
    Loader for a single image file.

    Provides functionality to load image data from a specified file path.
    """

    def __init__(self, path: str | Path) -> None:
        """
        Initialize the ImageFileLoader.

        Args:
            path: Path to the file to load (string or Path object)

        Raises:
            FileNotFoundError: If the specified path does not exist
            ValueError: If the specified path is a directory
        """
        if not Path(path).exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not Path(path).is_file():
            raise ValueError(f"Input path is directory path: {path}")
        self.file_path_guaranteed = Path(path)

    def load(self) -> ImageFileLoadResult:
        """
        Load the content of the file.

        Returns:
            ImageFileLoadResult: Result object containing the file path and its content
        """
        with Image.open(self.file_path_guaranteed) as image:
            return ImageFileLoadResult(
                path=self.file_path_guaranteed,
                value=image,
            )


class ImageFilesLoadResult(BaseModel):
    """
    Model representing the result of loading multiple image files.

    Attributes:
        directory_path: Path to the source directory
        value: List of results for each loaded file
    """

    directory_path: Path
    value: List[ImageFileLoadResult]


class ImageFilesLoader:
    """
    Loader for multiple image files in a directory.

    Recursively loads all .txt files in the specified directory.
    """

    def __init__(self, directory_path: Path, extensions: List[str]) -> None:
        """
        Initialize the ImageFilesLoader.

        Args:
            directory_path: Directory path to search for image files
            extensions: List of file extensions to load

        Raises:
            FileNotFoundError: If the specified path does not exist
            ValueError: If the specified path is a file
        """
        if not Path(directory_path).exists():
            raise FileNotFoundError(f"File not found: {directory_path}")
        if not Path(directory_path).is_dir():
            raise ValueError(f"Input path is file path: {directory_path}")
        self.directory_path = directory_path
        self.image_files_guaranteed = (
            PathSearcher.search_specific_extensions_paths_from_directory_path(
                path=directory_path, extensions=extensions
            )
        )

    def load(self) -> ImageFilesLoadResult:
        """
        Load all image files in the directory.

        Returns:
            ImageFilesLoadResult: Object containing the directory path and loading results for each file
        """
        results: List[ImageFileLoadResult] = []
        for image_file in self.image_files_guaranteed:
            results.append(
                ImageFileLoader(path=image_file).load(),
            )
        return ImageFilesLoadResult(
            directory_path=self.directory_path,
            value=results,
        )
