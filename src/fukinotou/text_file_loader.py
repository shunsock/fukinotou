from pathlib import Path
from typing import List

from pydantic import BaseModel

from .load_error import LoadingError
from .path_handler.path_searcher import PathSearcher


class TextFileLoadResult(BaseModel):
    """
    Model representing the result of loading a text file.

    Attributes:
        path: Path to the loaded file
        value: Content of the file
    """

    path: Path
    value: str


class TextFileLoader:
    """
    Loader for a single text file.

    Provides functionality to load text data from a specified file path.
    """

    @staticmethod
    def load(path: str | Path, encoding: str = "utf-8") -> TextFileLoadResult:
        """
        Load the content of the file.

        Returns:
            TextFileLoadResult: Result object containing the file path and its content
        """
        p = Path(path)
        if not p.is_file():
            raise LoadingError(
                original_exception=None,
                error_message=f"Input path is invalid: {path}",
            )
        try:
            content = p.read_text(encoding=encoding)
            return TextFileLoadResult(
                path=p,
                value=content,
            )
        except Exception as e:
            raise LoadingError(
                original_exception=e, error_message=f"Error reading file {path}: {e}"
            )


class TextFilesLoadResult(BaseModel):
    """
    Model representing the result of loading multiple text files.

    Attributes:
        path: Path to the source directory
        value: List of results for each loaded file
    """

    path: Path
    value: List[TextFileLoadResult]


class TextFilesLoader:
    """
    Loader for multiple text files in a directory.

    Recursively loads all .txt files in the specified directory.
    """

    @staticmethod
    def load(path: str | Path, encoding: str = "utf-8") -> TextFilesLoadResult:
        """
        Load all text files in the directory.

        Returns:
            TextFilesLoadResult: Object containing the directory path and loading results for each file
        """
        p = Path(path)
        if not p.is_dir():
            raise LoadingError(
                original_exception=None,
                error_message=f"Input path is invalid: {path}",
            )

        text_files: List[Path] = (
            PathSearcher.search_specific_extension_paths_from_directory_path(
                path=p,
                extension=".txt",
            )
        )

        # propagate LoadingError
        loader = TextFileLoader()
        results: List[TextFileLoadResult] = [
            loader.load(text_file) for text_file in text_files
        ]

        return TextFilesLoadResult(
            path=p,
            value=results,
        )
