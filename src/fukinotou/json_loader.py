from pathlib import Path
from typing import List, Type, TypeVar, Generic

import json
from pydantic import BaseModel

from .path_handler.path_searcher import PathSearcher

T = TypeVar('T', bound=BaseModel)


class JsonLoadResult(BaseModel, Generic[T]):
    """
    Model representing the result of loading a json file.

    Attributes:
        path: Path to the loaded file
        value: Content of the file
    """
    path: Path
    value: T


class JsonLoader(Generic[T]):
    def __init__(self, path: str | Path, model: Type[T]) -> None:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not p.is_file():
            raise ValueError(f"Input path is directory path: {path}")
        self.file_path = p
        self.model = model

    def load(self) -> JsonLoadResult[T]:
        with self.file_path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        parsed = self.model.model_validate(raw)
        return JsonLoadResult(path=self.file_path, value=parsed)


class JsonsLoadResult(BaseModel, Generic[T]):
    """
    Model representing the result of loading multiple json files.
    """
    directory_path: Path
    value: List[JsonLoadResult[T]]


class JsonsLoader(Generic[T]):
    def __init__(self, directory_path: str | Path, model: Type[T]) -> None:
        d = Path(directory_path)
        if not d.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        if not d.is_dir():
            raise ValueError(f"Input path is file path: {directory_path}")
        self.directory_path = d
        self.model = model
        self.json_files = PathSearcher.search_specific_extension_paths_from_directory_path(
            path=d,
            extension=".json",
        )

    def load(self) -> JsonsLoadResult[T]:
        results: List[JsonLoadResult[T]] = []
        for json_file in self.json_files:
            loader = JsonLoader(path=json_file, model=self.model)
            results.append(loader.load())
        return JsonsLoadResult(directory_path=self.directory_path, value=results)
