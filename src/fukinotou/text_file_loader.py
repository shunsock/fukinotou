from pathlib import Path
from typing import List

from pydantic import BaseModel

from .exception.loading_exception import LoadingException
from .path_handler.path_searcher import PathSearcher


class TextFileLoaded(BaseModel):
    """
    Model representing the result of loading a text file.

    Attributes:
        path: Path to the loaded file
        value: Content of the file
    """

    path: Path
    value: str


class TextFilesLoaded(BaseModel):
    """
    Model representing the result of loading multiple text files.

    Attributes:
        path: Path to the source directory
        value: List of results for each loaded file
    """

    path: Path
    value: List[TextFileLoaded]


class TextFileLoader:
    """
    Loader for a single text file.

    Provides functionality to load text data from a specified file path.
    """

    @staticmethod
    def load(path: str | Path, encoding: str = "utf-8") -> TextFileLoaded:
        """
        Load the content of the file.

        Returns:
            TextFileLoaded: Result object containing the file path and its content
        """
        p = Path(path)
        if not p.is_file():
            raise LoadingException(
                original_exception=None,
                error_message=f"Input path is invalid: {path}",
            )
        try:
            content = p.read_text(encoding=encoding)
            return TextFileLoaded(
                path=p,
                value=content,
            )
        except Exception as e:
            raise LoadingException(
                original_exception=e, error_message=f"Error reading file {path}: {e}"
            )


class TextFilesLoader:
    """
    Loader for multiple text files in a directory.

    Recursively loads all .txt files in the specified directory.
    """

    @staticmethod
    def load(path: str | Path, encoding: str = "utf-8") -> TextFilesLoaded:
        """
        Load all text files in the directory.

        Returns:
            TextFilesLoaded: Object containing the directory path and loading results for each file
        """
        p = Path(path)
        if not p.is_dir():
            raise LoadingException(
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
        results: List[TextFileLoaded] = [
            loader.load(text_file) for text_file in text_files
        ]

        return TextFilesLoaded(
            path=p,
            value=results,
        )
