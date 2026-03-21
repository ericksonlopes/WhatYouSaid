# Engineering Best Practices

Follow these standards across all generated code.

## General Principles
- **KISS (Keep It Simple, Stupid)**: Avoid over-engineering. Favor simple, readable solutions.
- **SOLID**: Follow object-oriented design principles (Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion).
- **Fail Fast**: Validate inputs and state early; throw descriptive errors.
- **Defensive Programming**: Handle potential `null` or `undefined` values gracefully.

## Python Specifics
- Use **PEP 8** style guidelines.
- Use **Type Hints** for all function signatures and complex variables.
- Prefer **list comprehensions** or generator expressions for simple iterations.
- Use `pathlib` for file system operations.
- Always use `with` blocks for resource management (files, sockets).

## TypeScript / JavaScript Specifics
- Prefer **functional programming** patterns (immutability, pure functions).
- Use strict typing; avoid `any` at all costs.
- Use `async/await` for asynchronous operations; avoid callback hell.
- Use modern ES6+ features (destructuring, spread operators, template literals).
- Follow standard naming conventions (PascalCase for classes/types, camelCase for variables/functions).

## Documentation
- Document complex logic with clear comments.
- Use Docstrings (Python) or JSDoc (JS/TS) for public APIs.
- Explain the "Why" behind non-obvious implementation choices.
