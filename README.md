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
from fukinotou import DataLoader
```
## Contributing
## Code Style
- **Type Annotations**: Always use type annotations. Use `typeguard` for 3rd party tools without types.
- **Docstrings**: Japanese docstrings for all classes and methods. Describe what the code does, not how. docstrings style must be Google style.
- **Classes**: Each class has a single responsibility. Public methods have tests.
- **Testing**: Use AAA pattern (Arrange-Act-Assert). Avoid mocks when possible. Clean up test objects.
- **Imports**: Standard library first, third-party second, local modules last.
- **Naming**: Use descriptive names in English. Classes are PascalCase, methods/functions are snake_case.
