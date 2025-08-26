# Byrdie Development Plan

This document outlines the development plan for byrdie, an opinionated Django wrapper designed for simplicity, productivity, and modern web development practices.

## I. Vision & Philosophy

*   **Core Mission:** To be the fastest way to build elegant, dynamic, and maintainable web applications with Python.
*   **Inspirations:** Django Cotton, Alpine.js, modern JavaScript frameworks (e.g., Vue, Svelte).
*   **Guiding Principles:**
    *   Convention over Configuration: Make strong, sensible assumptions to reduce boilerplate.
    *   Reduce Clutter: Abstract away Django's internal wiring where possible.
    *   Vertical Integration: Seamlessly blend backend logic, server-side rendering, and client-side interactivity.
    *   Progressive Enhancement: Start simple and add complexity only when needed. An entire app can be a single file, but it can also grow into a larger project.

## II. Core Features

### A. Simplified Entrypoint and Routing

*   **Goal:** Combine project setup, HTML page rendering, and API endpoint creation into a single, intuitive flow.
*   **Mechanism:**
    *   A single `runserver()` function starts the entire application.
    *   **Routes are defined using the `@route()` decorator.** The path argument is optional.
        *   **Explicit Path:** You can provide a path string, like `@route("/my-custom-path")`.
        *   **Implicit Path:** If no path is provided, Byrdie generates one from the function name. `index` is a special case that maps to `/`. For other functions, underscores are converted to dashes (`-`) and double underscores to slashes (`/`). For example, `def user__profile()` becomes `/user/profile`.
    *   **API routes are automatically prefixed.** If `api=True` is set, the final route will be automatically prefixed with `/api`. For example, `@route(api=True) def list_notes()` generates the path `/api/list-notes`.
    *   **API serialization is also automatic.**
        *   **Explicit Schema:** For complex cases, you can provide a Pydantic-style Schema in the function's return type hint (e.g., `-> list[MySchema]`). Byrdie will use this for serialization and API documentation.
        *   **Default Schema (Implicit):** If no schema is provided, Byrdie will create a default schema from the model fields that have `expose=True` set.

### B. Unified Model-Component Architecture

*   **Goal:** Unify the concepts of a database model and a renderable component, allowing a single model to have multiple, distinct presentation formats.
*   **Mechanism:**
    *   The `byrdie.Model` class is a superset of a standard Django model.
    *   **Default Component:** By convention, a model `class Note(Model)` is automatically associated with a default component, rendered with a `<note />` tag in templates, which loads `components/note.html`.
    *   **Named Components:** The model can define a `components = ["card", ...]` list to specify additional, named presentation formats.

### C. Hyper-Integrated Template Processor

*   **Goal:** Create a template rendering experience that is highly intuitive and context-aware, removing as much boilerplate as possible.
*   **Mechanism:**
    *   Byrdie includes a custom template processor that dynamically interprets tags based on the current context.
    *   **Default Tag:** Inside a `{% for note in notes %}` loop, `<note />` resolves to the default component for the `note` object.
    *   **Named Tag:** The syntax `<note:card />` resolves to the named "card" component for the `note` object, loading the `components/note_card.html` template.
    *   The relevant object (`note`) is implicitly passed into the component's template context.
    *   **Base Template Injection:** View templates are treated as body-only fragments by default. They are automatically injected into a base template that provides the `<html>` and `<body>` structure. To add content to the document `<head>`, a template can define a `{% block head %}`.

### D. Convention-Driven & Clutter-Free

*   **Goal:** Make the entire architecture implicit and predictable, guided by strong conventions.
*   **Conventions:**
    *   **Routing:** Use `@route()` to define a page or API endpoint. The path is optional and can be generated from the function name (e.g., `def user__profile()` becomes `/user/profile`). API routes (`api=True`) are automatically prefixed with `/api`.
    *   **HTML Rendering:** A view function that does not have `api=True` implicitly renders a template matching its name (e.g., `def index()` renders `templates/index.html`). The rendered template is injected as the `<body>` of a complete HTML document.
    *   **Components:** A model `class Note(Model)` maps to a `<note>` tag (`components/note.html`). An entry in its `components` list, e.g. `"card"`, maps to a `<note:card>` tag (`components/note_card.html`).
    *   **Directory Structure:** Component templates live in `components/`. Page templates live in `templates/`.

### E. The Byrdie Frontend Bridge

*   **Goal:** To seamlessly connect backend model logic with frontend interactivity. The bridge allows developers to write Python methods on their models and call them directly from the frontend, with data automatically synchronized.
*   **Mechanism:**
    *   **Activation:** The Frontend Bridge is activated by using a model's name as an HTML tag (e.g., `<note>`). This replaces the need for a generic `div` with a special attribute. For convenience, Byrdie will also automatically add the model's name as a CSS class to the rendered element (e.g., `class="note"`).
    *   **State:** Byrdie automatically initializes the component's data context by serializing the model's fields that are marked with `expose=True`. Purely client-side state can be added using `x-data`.
    *   **Exposed Methods:** Use the `@expose` decorator on a method in your `Model` class to make it callable from the frontend. This function becomes available via the `byrdie` object (e.g., `byrdie.save()`).
    *   **Data Sync:** When an exposed method is called, its arguments are sent to the backend. Byrdie runs the corresponding Python method. If the method returns a dictionary, Byrdie uses it to update the component's state on the frontend, automatically refreshing the UI.
    *   **Syntax:** The frontend bridge uses Alpine.js for its underlying reactivity and directives (`x-show`, `x-model`, `@click`, etc.).

#### Example: In-place Editing

Let's adapt the in-place editing example to this new, more elegant syntax.

**1. The Model: `app.py`**

The model definition remains the same, with `@expose` on the `save` method.

```python
# app.py (updated Note model)
from byrdie import Model, expose, models # ... etc

class Note(Model):
    text = models.CharField(max_length=255, expose=True)
    created_at = models.DateTimeField(auto_now_add=True, expose=True)

    class Meta:
        ordering = ["-created_at"]

    # This method is exposed to the frontend.
    @expose
    def save(self, new_text: str):
        # The new text is passed as an argument from the frontend.
        self.text = new_text
        self.save()
        # Return a dict to update the frontend component's state.
        # This will update 'text' and set 'is_editing' to false.
        return {"text": self.text, "is_editing": False}
```

**2. The Component Template: `components/note.html`**

The component template is now defined with the model's name as its root element. This activates the bridge.

```html
<!-- components/note.html -->
<note x-data="{ is_editing: false, edited_text: text }">
    <!-- Show this when not editing -->
    <div x-show="!is_editing">
        <p @dblclick="is_editing = true; edited_text = text">{{ text }}</p>
    </div>

    <!-- Show this when editing -->
    <div x-show="is_editing" x-cloak>
        <input type="text" x-model="edited_text">
        <button @click="byrdie.save(edited_text)">Save</button>
        <button @click="is_editing = false">Cancel</button>
    </div>

    <small>Created: {{ created_at|date:"M d, Y" }}</small>
</note>
```

### F. Concurrent by Default with Wove

*   **Goal:** Make structured concurrency a core, effortless part of development. Byrdie embraces a concurrent-by-default philosophy, powered by `curvedinf/wove`.
*   **Mechanism:**
    *   **Wove by Default:** The `wove` integration is enabled for all routes by default, injecting a `w` object into every view function. This encourages developers to write non-blocking code from the start.
    *   **Opt-out:** You can disable this behavior on a per-route basis by using `@route(wove=False)`.
    *   **Dependency Injection:** `wove` automatically builds a dependency graph of your tasks. If a task function has a parameter with the same name as another task, `wove` will wait for the dependency to finish and inject its result.
    *   **Automatic Context:** The view function does not need a `return` statement. Byrdie automatically executes the defined tasks and assembles the template context from their results.

#### Example: Dynamic Task Dependencies

This example demonstrates how `wove` can dynamically resolve dependencies. The `get_books_by_authors` task depends on the result of `get_popular_authors`, and `wove` will wait for the first task to complete before starting the second.

```python
# app.py (a view using wove)
from byrdie import route
from .models import Author, Book

@route() # wove is enabled by default
def author_showcase(request, w):
    # This task runs first, independently.
    @w.do
    def get_popular_authors() -> list[Author]:
        return Author.objects.filter(is_popular=True).limit(5)

    # This task depends on the result of the one above. Wove injects the
    # result by matching the parameter name `get_popular_authors` to the
    # function name of the task.
    @w.do
    def get_books_by_authors(get_popular_authors: list) -> dict:
        books_by_author = {}
        for author in get_popular_authors:
            # Assuming a related name of 'books' on the Author model
            books_by_author[author.name] = list(author.books.all())
        return books_by_author

    # No return statement is needed. The template context will be:
    # {
    #   'get_popular_authors': [...],
    #   'get_books_by_authors': {...}
    # }
```

**Template: `templates/author_showcase.html`**

The template receives the results of the `wove` tasks as top-level context variables.

```html
<!-- templates/books_and_authors.html -->
<h1>New Books and Popular Authors</h1>

<h2>New Releases</h2>
<ul>
    {% for book in new_releases %}
        <li>{{ book.title }}</li>
    {% endfor %}
</ul>

<h2>Popular Authors</h2>
<ul>
    {% for author in popular_authors %}
        <li>{{ author.name }}</li>
    {% endfor %}
</ul>
```

## III. Developer Experience (DX): The "Hello, Byrdie" App

The following files demonstrate the complete, polished developer experience, showcasing page rendering, multiple component views, and a JSON API endpoint in one cohesive application.

### A. The Application: `app.py`

```python
# app.py
import datetime
from byrdie import Model, route, runserver, models

# The Model defines the data structure. Fields with `expose=True`
# are automatically included in default API responses and are
# available to the Byrdie Frontend Bridge.
class Note(Model):
    text = models.CharField(max_length=255, expose=True)
    created_at = models.DateTimeField(auto_now_add=True, expose=True)

    # Defines an additional, named component view for this model.
    # This 'card' view will map to 'components/note_card.html'.
    components = ["card"]

    class Meta:
        ordering = ["-created_at"]

# The view for the root URL. The function name `index` is a special
# case that automatically maps to `/`.
# The `w` parameter is injected by default for concurrency.
@route()
def index(request, w):
    if not Note.objects.exists():
        Note.objects.create(text="This note is rendered by byrdie's magic!")
    return {"notes": Note.objects.all()}

# An API view. The route is implicitly generated from the function
# name as `/api/list-notes`. `w` is also available here.
@route(api=True)
def list_notes(request, w):
    return Note.objects.all()

# The entrypoint runs the server, including the web and API routes.
if __name__ == "__main__":
    runserver()
```

### B. The Page Template: `templates/index.html`

```html
<!-- templates/index.html -->
{% block head %}
    <title>My Notes</title>
{% endblock %}

<h1>My Notes</h1>
<div class="note-list">
    {% for note in notes %}
        <div style="margin-bottom: 2em; padding: 1em; border: 1px solid #ccc;">
            <p><strong>Default view (from <code>&lt;note /&gt;</code>):</strong></p>
            <!-- Renders the default component: 'components/note.html' -->
            <note />

            <hr style="margin: 1em 0;" />

            <p><strong>Card view (from <code>&lt;note:card /&gt;</code>):</strong></p>
            <!-- Renders the specific 'card' component: 'components/note_card.html' -->
            <note:card />
        </div>
    {% endfor %}
</div>
```

### C. The Component Templates

**Default component: `components/note.html`**
```html
<!-- components/note.html -->
<div class="note" style="border: 1px solid #ddd; padding: 1em; margin-bottom: 1em;">
    <p>{{ note.text }}</p>
    <small>Created: {{ note.created_at|date:"M d, Y" }}</small>
</div>
```

**Named component: `components/note_card.html`**
```html
<!-- components/note_card.html -->
<div class="note-card" style="background: #f0f0f0; padding: 0.5em;">
    <p><strong>Card:</strong> {{ note.text }}</p>
</div>
```

## IV. Technical Implementation Sketch

*   This section will be for brainstorming the "how." We'll think about the core `byrdie` application, the component rendering pipeline, and how we'll manage static assets.

## V. Roadmap

*   **Phase 1: Proof of Concept:**
    *   Build the `byrdie.quickstart()` entrypoint.
    *   Implement a basic component class and renderer.
    *   Successfully create and run the single-file "Hello, Byrdie" app.
*   **Phase 2: Core Feature Development:**
    *   Flesh out the component model (data binding, actions).
    *   Integrate Alpine.js helpers.
    *   Refine the URL routing.
*   **Phase 3: Alpha/Beta Release:**
    *   Package byrdie for PyPI.
    *   Write documentation.
    *   Gather community feedback.
