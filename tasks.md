# Byrdie Development Tasks

This document breaks down the development plan for the byrdie framework into deliverable tasks, based on the vision outlined in `plan.md`.

## Phase 1: Proof of Concept & Core Infrastructure

This phase focuses on establishing the basic scaffolding of the project and delivering a minimal, runnable "Hello, Byrdie" application.

-   [x] **Task 1.1: Initial Project Structure:** Set up the basic file and directory structure for the `byrdie` library.
-   [x] **Task 1.2: Command-Line Entrypoint:** Implement the `byrdie` command-line script to replace `manage.py`.
-   [x] **Task 1.3: `runserver()` Function:** Create the core `runserver()` function that starts the development server.
-   [x] **Task 1.4: Basic `byrdie.Model`:** Implement a foundational `Model` class that inherits from `django.db.models.Model` but is prepared for Byrdie's extensions.
-   [x] **Task 1.5: Basic Component Renderer:** Develop a simple template processor capable of rendering a model's default component (e.g., `<note />`).
-   [x] **Task 1.6: "Hello, Byrdie" Example:** Create the single-file `app.py` example application to validate the work of this phase.

## Phase 2: Core Feature Implementation

This phase focuses on building out the primary features that define the byrdie developer experience.

### Sub-phase 2.1: Simplified Routing & API
-   [x] **Task 2.1.1: `@route` Decorator:** Implement the `@route()` decorator with support for explicit paths (`@route("/path")`) and implicit, name-based paths (`def user__profile()`).
-   [x] **Task 2.1.2: API Prefixing:** Add the `api=True` argument to the `@route` decorator to automatically prefix routes with `/api`.
-   [x] **Task 2.1.3: Route-Level Security:** Implement the `is_authenticated=True` and `has_permissions=<callable>` arguments for the `@route` decorator.

### Sub-phase 2.2: Advanced API Serialization
-   [x] **Task 2.2.1: Explicit Schema Serialization:** Add support for Pydantic-style schemas in view return type hints (`-> list[MySchema]`) for automatic response serialization.
-   [x] **Task 2.2.2: Default Schema Generation:** Implement the logic to create a default serialization schema from a model's fields marked with `expose=True`.
-   [x] **Task 2.2.3: `ModelSchema`:** Implement the `ModelSchema` class to allow for defining alternate, reusable serialization views for existing models.
-   [x] **Task 2.2.4: Custom `Schema`:** Implement the `byrdie.Schema` class for defining arbitrary data structures for API responses.
-   [x] **Task 2.2.5: Schema-Owned Routes:** Implement the discovery mechanism for routes defined as methods on `Schema` and `ModelSchema` classes (both `@classmethod` for collections and instance methods for single items).

### Sub-phase 2.3: Unified Model-Component Architecture
-   [x] **Task 2.3.1: Default Component Convention:** Solidify the convention where a `Note` model maps to a `<note />` tag and `components/note.html`.
-   [x] **Task 2.3.2: Named Components:** Implement the `components = ["card"]` list on models to enable named component views like `<note:card />`.

### Sub-phase 2.4: Hyper-Integrated Template Processor
-   [x] **Task 2.4.1: Implicit Context Passing:** Ensure that when rendering a component (e.g., `<note />` inside a loop), the relevant object (`note`) is automatically passed into the component's template context.
-   [x] **Task 2.4.2: Base Template Injection:** Implement the logic that automatically injects view templates into a base template, and allows them to populate the `<head>` via `{% block head %}`.

### Sub-phase 2.5: The Byrdie Frontend Bridge
-   [x] **Task 2.5.1: Component Activation:** Implement the mechanism where using a model's name as an HTML tag (e.g., `<note>`) activates the frontend bridge.
-   [x] **Task 2.5.2: Automatic State Initialization:** Automatically serialize a model's `expose=True` fields and methods into the component's Alpine.js data scope.
-   [x] **Task 2.5.3: `@expose` Decorator:** Implement the `@expose` decorator to make Python model methods callable from the frontend.
-   [x] **Task 2.5.4: Proxied API Routes:** Create the global `byrdie` JavaScript object that exposes `@route(api=True)` functions, handling the full fetch/hydration lifecycle.
-   [x] **Task 2.5.5: Data Synchronization:** Implement the mechanism that takes a dictionary returned from an exposed Python method and uses it to update the frontend component's state.

### Sub-phase 2.6: Wove Integration
-   [ ] **Task 2.6.1: Wove by Default:** Integrate `wove` so that a `w` object is injected into all routes by default.
-   [ ] **Task 2.6.2: Automatic Context Assembly:** Implement the logic to automatically execute the `wove` task graph and assemble the template context from the results of named tasks.
-   [x] **Task 2.6.3: Session Management:** Add a setting for "remember me" session duration and a login view to implement it.

## Phase 3: Project Scalability & DX

This phase ensures that byrdie can grow from a single file into a larger, well-structured application and integrate with the existing Django ecosystem.

-   [ ] **Task 3.1: Modular Project Support:** Implement the discovery mechanism that finds routes and models in any modules imported into the main `app.py`.
-   [ ] **Task 3.2: `settings.py` Support:** Add logic to detect and load a standard Django `settings.py` file for configuration.
-   [ ] **Task 3.3: Django Integration:** Create the `byrdie.get_urls()` utility to allow an existing Django project to include and use routes defined with Byrdie.

## Phase 4: Release & Documentation

This phase focuses on packaging, documenting, and releasing the project.

-   [ ] **Task 4.1: PyPI Packaging:** Create the `setup.py` or `pyproject.toml` to package `byrdie` for distribution on PyPI.
-   [x] **Task 4.2: Comprehensive Documentation:** Write detailed documentation for every feature, including all classes, functions, and decorators.
-   [ ] **Task 4.3: Tutorials and Examples:** Create a set of tutorials and practical examples beyond the "Hello, Byrdie" app.
-   [ ] **Task 4.4: Community Feedback Channels:** Establish a process for gathering community feedback (e.g., GitHub Issues templates, discussions).
