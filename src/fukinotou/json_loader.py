from pathlib import Path
from typing import List, Type, TypeVar, Generic

import json

from pydantic import BaseModel, ValidationError

from .dataframe_exportable import DataframeExportable
from .load_error import LoadingError
from .path_handler.path_searcher import PathSearcher

T = TypeVar("T", bound=BaseModel)


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
    """Generic JSON file loader that validates content against a Pydantic model.

    This loader reads a JSON file and converts its content into an instance
    of a specified Pydantic model, performing validation during the conversion
    process.

    Type Parameters:
        T: A Pydantic BaseModel subclass that defines the schema for JSON content
    """

    def __init__(self, model: Type[T]) -> None:
        """Initialize the JSON loader with a target model class.

        Args:
            model: The Pydantic model class used to validate and parse JSON content
        """
        self.model = model

    def load(self, path: str | Path) -> JsonLoadResult[T]:
        """Load and validate data from a JSON file.

        Reads a JSON file, validates its content against the provided model class,
        and returns a structured result containing the validated content.

        Args:
            path: Path to the JSON file (string or Path object)

        Returns:
            JsonLoadResult containing the validated content as a model instance

        Raises:
            LoadingError: If the file doesn't exist, is a directory, contains invalid JSON,
                          or the content fails validation
        """
        p = Path(path)
        if not p.is_file():
            raise LoadingError(
                original_exception=None, error_message=f"Input path is invalid: {path}"
            )

        try:
            f = p.open("r", encoding="utf-8")
            raw = json.load(f)
            parsed = self.model.model_validate(raw)
        except json.JSONDecodeError as e:
            raise LoadingError(
                original_exception=e,
                error_message=f"Error parsing JSON file {path}: {e}",
            )
        except ValidationError as e:
            raise LoadingError(
                original_exception=e,
                error_message=f"Error validating JSON file {path}: {e}",
            )
        return JsonLoadResult(path=p, value=parsed)


class JsonsLoadResult(BaseModel, Generic[T], DataframeExportable):
    """Model representing the result of loading multiple JSON files.

    Attributes:
        path: Path to the directory from which files were loaded
        value: List of JSON load results, each containing a model instance
    """

    path: Path
    value: List[JsonLoadResult[T]]


class JsonsLoader(Generic[T]):
    """Generic JSON directory loader that validates multiple JSON files against a Pydantic model.

    This loader scans a directory for JSON files and converts each file's content
    into an instance of a specified Pydantic model, performing validation during
    the conversion process.

    Type Parameters:
        T: A Pydantic BaseModel subclass that defines the schema for JSON content
    """

    def __init__(self, model: Type[T]) -> None:
        """Initialize the JSONs loader with a target model class.

        Args:
            model: The Pydantic model class used to validate and parse JSON content
        """
        self.model = model

    def load(self, directory_path: str | Path) -> JsonsLoadResult[T]:
        """Load and validate data from all JSON files in a directory.

        Scans a directory for JSON files, reads each file, validates its content
        against the provided model class, and returns a structured result containing
        all the validated content. Files that fail to parse or validate are strictly prohibited.

        Args:
            directory_path: Path to the directory containing JSON files (string or Path object)

        Returns:
            JsonsLoadResult containing all the successfully validated content as model instances

        Raises:
            LoadingError: If the directory doesn't exist or is not a directory or validation failed
        """
        d = Path(directory_path)
        if not d.is_dir():
            raise LoadingError(
                original_exception=None,
                error_message=f"Input path is not directory: {d}",
            )

        json_files: List[Path] = (
            PathSearcher.search_specific_extension_paths_from_directory_path(
                path=d,
                extension=".json",
            )
        )

        # Raise Error if we found any invalid rows
        loader = JsonLoader(model=self.model)
        results: List[JsonLoadResult[T]] = [
            loader.load(json_file) for json_file in json_files
        ]

        return JsonsLoadResult(path=d, value=results)
