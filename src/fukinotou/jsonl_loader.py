from pathlib import Path
from typing import List, Type, TypeVar, Generic
import json
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class JsonlLoadResult(BaseModel, Generic[T]):
    """
    Model representing the result of loading a JSONL file.

    Attributes:
        path: Path to the loaded file
        values: List of parsed model instances (one per line)
    """

    path: Path
    values: List[T]


class JsonlLoader(Generic[T]):
    """
    Loader for JSONL (JSON Lines) files that parses each line into the specified Pydantic model.

    This loader reads a JSONL file line by line, parses each valid JSON line, and validates
    it against the provided Pydantic model. Empty lines are skipped. The loader will raise
    exceptions for file not found, invalid paths, and JSON parsing errors.
    """

    def __init__(self, file_path: str | Path, model: Type[T]) -> None:
        p = Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not p.is_file():
            raise ValueError(f"Input path is a directory, not a file: {file_path}")
        self.file_path = p
        self.model = model

    def load(self) -> JsonlLoadResult[T]:
        """
        Load and parse the JSONL file into model instances.

        This method reads the JSONL file, parses each non-empty line as JSON,
        validates it against the specified Pydantic model, and returns
        a JsonlLoadResult containing the file path and a list of all
        successfully parsed model instances.

        Returns:
            JsonlLoadResult[T]: Result object containing the file path and list of model instances

        Raises:
            ValueError: If any line contains invalid JSON or fails model validation
        """
        values: List[T] = []
        with self.file_path.open("r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, start=1):
                raw = line.strip()
                if not raw:
                    continue  # skip empty lines
                try:
                    obj = json.loads(raw)
                except json.JSONDecodeError as e:
                    raise ValueError(
                        f"Invalid JSON on line {lineno} of {self.file_path}: {e}"
                    ) from e
                parsed = self.model.model_validate(obj)
                values.append(parsed)

        return JsonlLoadResult(path=self.file_path, values=values)
