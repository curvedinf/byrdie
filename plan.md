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
    *   Routes are defined using the `@route("/")` decorator. Byrdie automatically discovers and registers them.
    *   The decorator includes an `api=True` parameter that switches its behavior from an HTML-rendering view to a JSON API endpoint, with functionality inspired by Django Ninja (automatic serialization, API documentation, etc.).

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

### D. Convention-Driven & Clutter-Free

*   **Goal:** Make the entire architecture implicit and predictable, guided by strong conventions.
*   **Conventions:**
    *   **Routing:** `@route("/")` defines a page or API endpoint. An `api=True` parameter switches between the two.
    *   **HTML Rendering:** A view function that does not have `api=True` implicitly renders a template matching its name (e.g., `def index()` renders `templates/index.html`) by returning a context dictionary.
    *   **Components:** A model `class Note(Model)` maps to a `<note>` tag (`components/note.html`). An entry in its `components` list, e.g. `"card"`, maps to a `<note:card>` tag (`components/note_card.html`).
    *   **Directory Structure:** Component templates live in `components/`. Page templates live in `templates/`.

## III. Developer Experience (DX): The "Hello, Byrdie" App

The following files demonstrate the complete, polished developer experience, showcasing page rendering, multiple component views, and a JSON API endpoint in one cohesive application.

### A. The Application: `app.py`

```python
# app.py
import datetime
from byrdie import Model, route, runserver, models, Schema

# A Pydantic-style schema for the API endpoint
class NoteSchema(Schema):
    text: str
    created_at: datetime.datetime

# The Model defines the data structure and its component views.
class Note(Model):
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    # Defines an additional, named component view for this model.
    # This 'card' view will map to 'components/note_card.html'.
    components = ["card"]

    class Meta:
        ordering = ["-created_at"]

# View for the HTML page
@route("/")
def index(request):
    if not Note.objects.exists():
        Note.objects.create(text="This note is rendered by byrdie's magic!")
    return {"notes": Note.objects.all()}

# View for the JSON API
@route("/api/notes", api=True)
def list_notes(request) -> list[NoteSchema]:
    return Note.objects.all()

# The entrypoint runs the server, including the web and API routes.
if __name__ == "__main__":
    runserver()
```

### B. The Page Template: `templates/index.html`

```html
<!-- templates/index.html -->
<html>
<body>
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
</body>
</html>
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
