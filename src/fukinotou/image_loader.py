from pathlib import Path
from typing import List

from pydantic import BaseModel, ConfigDict
from PIL import Image

from .load_error import LoadingError
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

    @staticmethod
    def load(path: str | Path) -> ImageFileLoadResult:
        """
        Load the content of the file.

        Returns:
            ImageFileLoadResult: Result object containing the file path and its content
        """
        p = Path(path)
        if not Path(p).exists():
            raise LoadingError(
                original_exception=None, error_message=f"File not found: {p}"
            )
        if not Path(p).is_file():
            raise LoadingError(
                original_exception=None,
                error_message=f"Input path is directory path: {p}",
            )
        try:
            image = Image.open(p)
            return ImageFileLoadResult(
                path=p,
                value=image,
            )
        except Exception as e:
            raise LoadingError(
                original_exception=e, error_message=f"Error reading file {p}: {e}"
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

    Recursively loads all image files with specified extensions in the given directory.
    """

    @staticmethod
    def load(path: str | Path, extensions: List[str]) -> ImageFilesLoadResult:
        """
        Load all image files in the directory.

        Returns:
            ImageFilesLoadResult: Object containing the directory path and loading results for each file
        """
        p = Path(path)
        if not p.exists():
            raise LoadingError(
                original_exception=None, error_message=f"File not found: {p}"
            )
        if not p.is_dir():
            raise LoadingError(
                original_exception=None,
                error_message=f"Input path is file path: {p}",
            )

        image_file_paths: List[Path] = (
            PathSearcher.search_specific_extensions_paths_from_directory_path(
                path=p, extensions=extensions
            )
        )

        results: List[ImageFileLoadResult] = [
            ImageFileLoader().load(image_file) for image_file in image_file_paths
        ]
        return ImageFilesLoadResult(
            directory_path=p,
            value=results,
        )
