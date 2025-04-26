# Fukinotou

Fukinotou is a Data Loader that we can inject our domain model.

## Why Fukinotou

### Validated during loading, but not afterward

Nowadays, validating data is a common idea before transforming or exporting. And we also have Pydantic Models in application.
If you are FastAPI user, you may see the following code.

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

### Path Information is combined with loaded values

Path information is important when debugging analysis. Fukinotou protests your path information.

```python
from fukinotou import CsvLoader, CsvLoaded

users: CsvLoaded[Visitor] = CsvLoader(Visitor).load("./visitor.csv")
print(users.path)
print(users[0].path) # you can ith of row value with users[i].value
```

### Export to Dataframe

We often export collections to dataframe object (such as `pandas`, `polars`, and so on).

Tackling the issue, we also provide method `to_polars` and `to_pandas` to convert the loaded data into Polars or Pandas Dataframe through `DataframeExportable`
Thus, we can export easily, by calling these methods from class inheriting `DataframeExportable` (ex: `JsonsLoaded`).

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
