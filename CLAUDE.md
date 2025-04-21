# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Test/Lint Commands
- Install: `task install`
- Install dev dependencies: `task install-dev`
- Run lints: `task lint`
- Run formatting: `task format`
- Run type checking: `task typecheck`
- Run tests: `task test`
- Run single test: `task test-one -- tests/test_file.py::test_function_name`

## Code Style Guidelines
- **Type Annotations**: Required for all code (enforced with mypy and py.typed)
- **Docstrings**: Use Google style docstrings in Japanese
- **Classes**: Follow single responsibility principle, public methods need tests
- **Testing**: Use AAA pattern (Arrange-Act-Assert), avoid mocks, clean up test objects
- **Imports Order**: 1) Standard library, 2) Third-party, 3) Local modules
- **Naming**: Classes use PascalCase, methods/functions use snake_case
- **Error Handling**: Use appropriate exception types, provide meaningful error messages
- **Documentation**: Document public APIs thoroughly in English

This is a Python data loader package that focuses on simplicity and type safety.