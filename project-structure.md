# Byrdie Project Structure

This document outlines the architectural philosophy, core components, and proposed directory structure for the Byrdie framework.

## 1. Philosophy & Goals

*   **Simplicity and Productivity:** Byrdie's primary goal is to be the fastest way to build elegant, dynamic, and maintainable web applications in Python. It prioritizes convention over configuration to reduce boilerplate and cognitive overhead.
*   **Extensibility and Maintainability:** Byrdie is designed as a lightweight layer on top of Django. This allows applications built with Byrdie to be easily updated and maintained. The core framework will provide a stable, well-defined compatibility layer, abstracting away Django's internal complexities and providing a consistent API even as Django evolves.
*   **Performance by Default:** Byrdie embraces a concurrent-by-default philosophy and assumes a high-performance caching layer is always available. Features are designed from the ground up to be fast and efficient.

## 2. Core Technology Stack & Integration

### Django

Byrdie is not a replacement for Django, but a highly opinionated wrapper around it.
*   **Compatibility Layer:** It will sit on top of Django, providing simplified interfaces for routing, models, and rendering. This layer will be responsible for translating Byrdie's conventions into Django's required patterns.
*   **Eject Button:** While not a primary goal for the initial version, the architecture should eventually allow for a graceful "ejection" where a Byrdie project could be converted into a standard Django project if needed.

### Wove

Concurrency is a first-class citizen in Byrdie, powered by `wove`.
*   **Liberal Integration:** Wove will be used liberally throughout the Python codebase for all I/O-bound operations (database queries, API calls, etc.) to minimize latency. View functions will be concurrent by default.
*   **Framework Bootstrapping:** A key architectural goal is to use Wove to accelerate Django's own internals. Research will be done to identify opportunities to parallelize parts of Django's request-response cycle or even its initialization process, potentially leading to significant performance gains.

## 3. Template Engine & Caching

### Custom Template Processor

Byrdie will feature a custom-built template and component preprocessor.
*   **Cotton-Inspired:** It will not use Django Cotton as a dependency but will be designed to closely replicate its powerful features, such as the ability to resolve and render components directly from model names (e.g., `<note />`).
*   **Implicit Context:** The processor will automatically pass the relevant object context into component templates, reducing boilerplate.

### Multi-tier Caching

Caching is a foundational assumption in Byrdie, not an optional add-on. The framework is designed to be fast by aggressively caching rendered components and query results.
*   **Deep Integration:** The template preprocessor will be tightly integrated with the caching system to automatically cache rendered HTML fragments.
*   **Multi-tier Architecture:** Byrdie will ship with a built-in, multi-tier caching system.
    *   **L1 Cache (In-Memory):** A per-process, in-memory dictionary for extremely fast, short-lived caching within a single request or worker process.
    *   **L2 Cache (Database):** A database-backed cache for sharing cached data across processes and persisting it between requests.
*   **Configurability:** The entire caching system will be configurable, allowing developers to replace the default backends or add new tiers (e.g., Redis, Memcached) to suit their needs.

## 4. Frontend Strategy

### Alpine.js

Byrdie's frontend interactivity will be powered by Alpine.js.
*   **Git Submodule:** To ensure version consistency and simplify offline development, the Alpine.js source code will be included directly in the Byrdie project as a **git submodule** located at `byrdie/vendor/alpinejs`.
*   **Custom Wrapper:** A Byrdie-specific JavaScript wrapper (`byrdie/static/js/byrdie-alpine.js`) will be created. This script will be responsible for:
    *   Initializing Alpine.js.
    *   Creating the global `byrdie` JavaScript object.
    *   Providing helper functions to bridge the gap between Byrdie's backend (e.g., proxied API routes) and Alpine's reactive frontend components.

## 5. Proposed Development Directory Structure

This structure represents the repository for the Byrdie framework itself.

```
byrdie/
├── src/
│   └── byrdie/             # The main package source code
│       ├── __init__.py     # Public API
│       ├── routing.py      # @route decorator, etc.
│       ├── models.py       # Byrdie Model base class
│       ├── renderer/       # Custom template/component engine
│       │   ├── __init__.py
│       │   ├── processor.py
│       │   └── cache.py    # Multi-tier caching
│       ├── static/
│       │   └── js/
│       │       └── byrdie-alpine.js # Alpine.js wrapper
│       └── vendor/
│           └── alpinejs/   # Git submodule for Alpine.js source
├── tests/                  # Unit and integration tests
│   ├── __init__.py
│   └── test_routing.py
├── examples/               # Example Byrdie applications
│   └── hello_world/
│       ├── app.py
│       ├── templates/
│       └── components/
├── docs/                   # Project documentation (like this file)
│   └── project-structure.md
├── pyproject.toml          # Project metadata, dependencies (e.g., django, wove)
├── README.md
└── .gitignore
```
