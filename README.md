# Fukinotou

A simple Data Loader for Python.

## Install

You can install Fukinotou directly from GitHub using uv or pip.

### Using uv (recommended):

```shell
uv pip install git+https://github.com/shunsock/fukinotou.git
```

To install a specific version/tag, use:

```shell
uv pip install git+https://github.com/shunsock/fukinotou.git@<tag-name>
```

### Using pip:

```shell
pip install git+https://github.com/shunsock/fukinotou.git
```

## Usage

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
   pandas_df: pandas.DataFrame = users.to_pandas(include_path_as_column=True)
except FileNotFoundError as e:
    print(f"Error loading data at reading phase: {e}")
except ValueError as e:
   print(f"Error loading data at validation phase: {e}")
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
