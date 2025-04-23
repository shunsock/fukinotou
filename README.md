# Fukinotou

## About

Fukinotou is a simple data loader with validation capabilities. You can supply data path and a Pydantic model, and it will load the data into `*LoadResult` object which contains the validated data and path information.

```python
class JsonLoadResult(BaseModel, Generic[T]):
    path: Path
    value: T
```

We also provide method `to_polars` and `to_pandas` to convert the loaded data into Polars or Pandas DataFrame.

```python
class JsonsLoadResult(BaseModel, Generic[T]):
    directory_path: Path
    value: List[JsonLoadResult[T]]

    def to_polars(self, include_path_as_column: bool = False) -> polars.DataFrame:
        # ...
        return df

    def to_pandas(self, include_path_as_column: bool = False) -> pandas.DataFrame:
        # ...
        return df
```

## Install

You can install Fukinotou directly from GitHub using uv or pip.

### Requirements

Python 3.10 or later is required.

### Using uv (recommended):

```shell
uv pip install git+https://github.com/shunsock/fukinotou.git
```

🚧 **Under Construction**
- You can not use this feature currently, use above option instead.
- To install a specific version/tag, use:

```shell
uv pip install git+https://github.com/shunsock/fukinotou.git@<tag-name>
```

### Using pip:

```shell
pip install git+https://github.com/shunsock/fukinotou.git
```

## Usage

### Example

You can load CSV files using `CsvLoader`. It will automatically validate the data against the provided Pydantic model.

```python
from fukinotou import CsvLoader, CsvLoadResult
from pydantic import BaseModel
import polars
import pandas

class User(BaseModel):
    id: int
    name: str
    age: int

try:
   users: CsvLoadResult[User]  = CsvLoader("./data.csv", User).load()
   polars_df: polars.DataFrame = users.to_polars(include_path_as_column=False)
   print(polars_df)
   pandas_df: pandas.DataFrame = users.to_pandas(include_path_as_column=True)
   print(pandas_df)
except FileNotFoundError as e:
    print(f"Error loading data at reading phase: {e}")
except ValueError as e:
   print(f"Error loading data at validation phase: {e}")
```

This is output of the above code:

```shell
Loading data from CSV file...
shape: (3, 3)
┌─────┬─────────────┬─────┐
│ id  ┆ name        ┆ age │
│ --- ┆ ---         ┆ --- │
│ i64 ┆ str         ┆ i64 │
╞═════╪═════════════╪═════╡
│ 1   ┆ John Doe    ┆ 30  │
│ 2   ┆ Jane Smith  ┆ 25  │
│ 3   ┆ Bob Johnson ┆ 40  │
└─────┴─────────────┴─────┘
   id         name  age      path
0   1     John Doe   30  data.csv
1   2   Jane Smith   25  data.csv
2   3  Bob Johnson   40  data.csv
```

### Supported Loaders

```python
from fukinotou.text_file_loader import (
    TextFileLoadResult,
    TextFileLoader,
    TextFilesLoadResult, # read files under directory at once
    TextFilesLoader,
)
from fukinotou.json_loader import (
    JsonLoadResult,
    JsonLoader,
    JsonsLoadResult, # read files under directory at once
    JsonsLoader,
)
from fukinotou.jsonl_loader import (
    JsonlLoadResult,
    JsonlLoader,
)
from fukinotou.csv_loader import (
    CsvLoadResult,
    CsvLoader,
)
from fukinotou.parquet_loader import (
    ParquetLoadResult,
    ParquetLoader,
)
from fukinotou.image_loader import (
   ImageFileLoadResult,
   ImageFileLoader,
   ImageFilesLoadResult,
   ImageFilesLoader,
)
```

## Development

### Taskfile for Developing

This project uses [Task](https://taskfile.dev/) for managing development tasks. Here are the available commands:

- `task install` - Install package in development mode
- `task install-dev` - Install development dependencies
- `task lint` - Run linters
- `task format` - Format code
- `task typecheck` - Run type checking
- `task test` - Run all tests
- `task test-one -- tests/test_file.py::test_function_name` - Run a specific test

**Recommended Execution Order:**

1. First time setup: `task install-dev` (installs package with development dependencies)
2. Before submitting changes: 
   - `task format` (auto-formats code)
   - `task lint` (checks for code style issues)
   - `task typecheck` (verifies type annotations)
   - `task test` (runs all tests to ensure functionality)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

