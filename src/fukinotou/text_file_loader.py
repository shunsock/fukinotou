from pathlib import Path
from typing import List

from pydantic import BaseModel

from .path_handler.path_searcher import PathSearcher


class TextFileLoadResult(BaseModel):
    path: Path
    value: str


class TextFileLoader:
    def __init__(self, path: str | Path) -> None:
        if not Path(path).exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not Path(path).is_file():
            raise ValueError(f"Input path is directory path: {path}")
        self.file_path_guaranteed = Path(path)

    def load(self) -> TextFileLoadResult:
        with open(self.file_path_guaranteed, "r", encoding="utf-8") as f:
            return TextFileLoadResult(
                path=self.file_path_guaranteed,
                value=f.read(),
            )


class TextFilesLoadResult:
    directory_path: Path
    value: List[TextFileLoadResult]


class TextFilesLoader:
    def __init__(self, directory_path: Path) -> None:
        if not Path(directory_path).exists():
            raise FileNotFoundError(f"File not found: {directory_path}")
        if not Path(directory_path).is_dir():
            raise ValueError(f"Input path is directory path: {directory_path}")
        self.text_files_guaranteed = (
            PathSearcher.search_specific_extension_paths_from_directory_path(
                path=directory_path,
                extension=".txt",
            )
        )

    def load(self) -> TextFilesLoadResult:
        results: List[TextFileLoadResult] = []
        for text_file in self.text_files_guaranteed:
            results.append(
                TextFileLoader(path=text_file).load(),
            )
        return TextFilesLoadResult()
