from pathlib import Path
from typing import List

from pydantic import BaseModel

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

    def __init__(self, path: str | Path) -> None:
        """
        Initialize the TextFileLoader.

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

    def load(self) -> TextFileLoadResult:
        """
        Load the content of the file.

        Returns:
            TextFileLoadResult: Result object containing the file path and its content
        """
        with open(self.file_path_guaranteed, "r", encoding="utf-8") as f:
            return TextFileLoadResult(
                path=self.file_path_guaranteed,
                value=f.read(),
            )


class TextFilesLoadResult(BaseModel):
    """
    Model representing the result of loading multiple text files.

    Attributes:
        directory_path: Path to the source directory
        value: List of results for each loaded file
    """

    directory_path: Path
    value: List[TextFileLoadResult]


class TextFilesLoader:
    """
    Loader for multiple text files in a directory.

    Recursively loads all .txt files in the specified directory.
    """

    def __init__(self, directory_path: Path) -> None:
        """
        Initialize the TextFilesLoader.

        Args:
            directory_path: Directory path to search for text files

        Raises:
            FileNotFoundError: If the specified path does not exist
            ValueError: If the specified path is a file
        """
        if not Path(directory_path).exists():
            raise FileNotFoundError(f"File not found: {directory_path}")
        if not Path(directory_path).is_dir():
            raise ValueError(f"Input path is file path: {directory_path}")
        self.directory_path = directory_path
        self.text_files_guaranteed = (
            PathSearcher.search_specific_extension_paths_from_directory_path(
                path=directory_path,
                extension=".txt",
            )
        )

    def load(self) -> TextFilesLoadResult:
        """
        Load all text files in the directory.

        Returns:
            TextFilesLoadResult: Object containing the directory path and loading results for each file
        """
        results: List[TextFileLoadResult] = []
        for text_file in self.text_files_guaranteed:
            results.append(
                TextFileLoader(path=text_file).load(),
            )
        return TextFilesLoadResult(
            directory_path=self.directory_path,
            value=results,
        )
