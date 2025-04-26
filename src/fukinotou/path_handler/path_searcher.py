from pathlib import Path
from typing import List


class PathSearcher:
    @staticmethod
    def search_file_paths_from_directory_path(path: Path) -> List[Path]:
        """
        Search for all files in a directory.

        Args:
            path: The directory path to search

        Returns:
            A list of Path objects for files found
        """
        if not path.exists():
            return []

        if path.is_file():
            return [path]

        file_paths: List[Path] = []
        for item in path.iterdir():
            if item.is_file():
                file_paths.append(item)

        return file_paths

    @staticmethod
    def search_specific_extension_paths_from_directory_path(
        path: Path, extension: str
    ) -> List[Path]:
        """
        Search for files with a specific extension in a directory and its subdirectories.

        Args:
            path: The directory path to search
            extension: The file extension to search for (e.g., ".jpg", "txt")

        Returns:
            A list of Path objects for files with the specified extension
        """
        all_files = PathSearcher.search_file_paths_from_directory_path(path)

        if extension and not extension.startswith("."):
            extension = f".{extension}"

        return [file for file in all_files if file.suffix.lower() == extension.lower()]

    @staticmethod
    def search_specific_extensions_paths_from_directory_path(
        path: Path, extensions: List[str]
    ) -> List[Path]:
        """
        Search for files with multiple specific extensions in a directory and its subdirectories.

        Args:
            path: The directory path to search
            extensions: List of file extensions to search for (e.g., [".txt", ".png", ".pdf"])

        Returns:
            A list of Path objects for files with any of the specified extensions
        """
        all_files = PathSearcher.search_file_paths_from_directory_path(path)

        normalized_extensions = []
        for extension in extensions:
            if extension and not extension.startswith("."):
                normalized_extensions.append(f".{extension}")
            else:
                normalized_extensions.append(extension)

        return [
            file
            for file in all_files
            if any(file.suffix.lower() == ext.lower() for ext in normalized_extensions)
        ]
