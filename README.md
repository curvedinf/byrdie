# Byrdie

Byrdie is an opinionated Django wrapper designed for simplicity, productivity, and modern web development practices. It streamlines the development of web applications by reducing boilerplate and integrating seamlessly with Django, Wove for concurrency, and Alpine.js for frontend interactivity.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd byrdie
   ```

2. Set up the virtual environment and install dependencies:
   ```bash
   ./setup_dev.sh
   ```

3. Run the development server:
   ```bash
   byrdie runserver
   ```

## Usage

Byrdie allows you to define models, routes, and components in a single file (`app.py`) for rapid prototyping. See the [examples](examples/) directory for tutorials and the [documentation](docs/) for detailed guides.

For a simple "Hello, Byrdie" app:

- Define a model in `app.py`.
- Create component templates in `components/`.
- Run `byrdie runserver`.

## Contributing

We welcome contributions to Byrdie! To get started:

- **Report Bugs**: Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md) to file issues.
- **Request Features**: Suggest new ideas via the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md).
- **Join Discussions**: Participate in community conversations in the [Discussions tab](.github/DISCUSSIONS.md).

Please follow our code of conduct and ensure your pull requests include tests and documentation updates.

## Documentation

Full documentation is available in the [docs](docs/) directory, including getting started guides, core concepts, and API reference.

## License

MIT License. See [LICENSE](LICENSE) for details.

