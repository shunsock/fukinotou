# Fukinotou

Fukinotou is a Data Loader that we can validate with our domain model.

## Why Fukinotou

### Validated during loading, but not afterward

Data validation before transformation or export is a common requirement in modern applications, and Pydantic Models are
widely used for this purpose. If you are FastAPI user, you may see the following code.

```python
class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None
```

Fukinotou is a package to validate file content with our Pydantic Model.

```python
from fukinotou import JsonLoader, JsonLoaded

# JsonLoaded[ OUR_PYDANTIC_MODEL ]
users: JsonLoaded[Visitor] = JsonLoader(Visitor).load("./visitor.json")
```

This means, we can treat loaded data reliable if a loading process is succeeded.

### Path Information is combined with loaded values

Path information is crucial for debugging during analysis. Fukinotou preserves your path information throughout the
process. This is an example of reading logfiles under "./". 

```python
from fukinotou import JsonsLoader, JsonsLoaded

logfiles: JsonsLoaded[LogFileFormat] = JsonsLoader(LogfileFormat).load("./")
print(logfiles.path) # show directory path
print(logfiles.value[1].value.path) # show i-th log file path (not directory)
print(logfiles.value[1].value.value) # show i-th log file value
```

### Export to Dataframe

Converting data collections to DataFrame objects (like `pandas` or `polars`) is a common requirement.

To simplify this process, we provide `to_polars` and `to_pandas` methods through the `DataframeExportable` interface.
Any class that inherits from `DataframeExportable` (such as `JsonsLoaded`) can easily export data to these DataFrame
formats.

```python
from fukinotou import JsonLoader, JsonsLoaded
import polars
users: JsonsLoaded[Visitor] = JsonLoader(Visitor).load("./path_to_dir")
polars_df: polars.DataFrame = users.to_polars(include_path_as_column=False)
```

## Install

You can install Fukinotou directly from GitHub using uv or pip.

### Requirements

Python 3.10 or later is required.

### Using uv (recommended):

You can install by command below

```shell
uv pip install git+https://github.com/shunsock/fukinotou.git
```

or add following code to `pyproject.toml` and run `uv sync`

```
dependencies = [
    "fukinotou @ git+https://github.com/shunsock/fukinotou.git@v1.2.3"
    # you can also specify a branch or commit hash:
    # "fukinotou @ git+https://github.com/shunsock/fukinotou.git@branch"
    # "fukinotou @ git+https://github.com/shunsock/fukinotou.git@commit_hash"
]
```

### Using pip:

```shell
pip install git+https://github.com/shunsock/fukinotou.git
```

## Usage

### Example

You can load CSV files using `CsvLoader`. It will automatically validate the data against the provided Pydantic model.

```python
from fukinotou import CsvLoader, CsvLoaded, LoadingException
from pydantic import BaseModel
import polars
import pandas


class User(BaseModel):
   id: int
   name: str
   age: int


try:
   users: CsvLoaded[User] = CsvLoader(User).load("./users.csv")
   polars_df: polars.DataFrame = users.to_polars(include_path_as_column=False)
   print(polars_df)
   pandas_df: pandas.DataFrame = users.to_pandas(include_path_as_column=True)
   print(pandas_df)
except LoadingException as e:
   print(f"Failed to load: {e}")
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
    TextFileLoader,
    TextFilesLoader,
)
from fukinotou.json_loader import (
    JsonLoader,
    JsonsLoader,
)
from fukinotou.jsonl_loader import (
    JsonlLoader,
)
from fukinotou.csv_loader import (
    CsvLoader,
)
from fukinotou.parquet_loader import (
    ParquetLoader,
)
from fukinotou.image_loader import (
    ImageLoader,
    ImagesLoader,
)
```

## Development

Thank you for your interest in contributing to Fukinotou!
Here are some guidelines to help you get started:

### Branch

You can pull requests to `develop` branch. `main` branch is used for release.

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
