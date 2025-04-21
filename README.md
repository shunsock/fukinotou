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

### Coding Style
- **Type Annotations**: Always use type annotations. Use `typeguard` for 3rd party tools without types.
- **Docstrings**: Japanese docstrings for all classes and methods. Describe what the code does, not how. docstrings style must be Google style.
- **Classes**: Each class has a single responsibility. Public methods have tests.
- **Testing**: Use AAA pattern (Arrange-Act-Assert). Avoid mocks when possible. Clean up test objects.
- **Imports**: Standard library first, third-party second, local modules last.
- **Naming**: Use descriptive names in English. Classes are PascalCase, methods/functions are snake_case.
