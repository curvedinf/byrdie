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
    *   **Command-Line Entrypoint:** The standard `manage.py` script is replaced by a `byrdie` command provided by the package. Common tasks are run through it, e.g., `byrdie runserver`.
    *   A single `runserver()` function starts the entire application.
    *   **Routes are defined using the `@route()` decorator.** The path argument is optional.
        *   **Explicit Path:** You can provide a path string, like `@route("/my-custom-path")`.
        *   **Implicit Path:** If no path is provided, Byrdie generates one from the function name. `index` is a special case that maps to `/`. For other functions, underscores are converted to dashes (`-`) and double underscores to slashes (`/`). For example, `def user__profile()` becomes `/user/profile`.
    *   **API routes are automatically prefixed.** If `api=True` is set, the final route will be automatically prefixed with `/api`. For example, `@route(api=True) def list_notes()` generates the path `/api/list-notes`.
    *   **API serialization is also automatic.**
        *   **Explicit Schema:** For complex cases, you can provide a Pydantic-style Schema in the function's return type hint (e.g., `-> list[MySchema]`). Byrdie will use this for serialization and API documentation.
        *   **Default Schema (Implicit):** If no schema is provided, Byrdie will create a default schema from the model fields that have `expose=True` set.
    *   **Route-level Security:** Routes can be secured directly within the decorator.
        *   **Authentication Check:** Use `@route(is_authenticated=True)` to ensure that only logged-in users can access a view. If the user is not authenticated, they will be redirected to the login page.
        *   **Permission Check:** For more granular control, use `@route(has_permissions=...)`. This parameter accepts a callable (e.g., a function) that takes the `request` object as an argument and should return `True` if the user has permission, and `False` otherwise. If the check fails, a 403 Forbidden error is returned.

        ```python
        # A simple authentication check
        @route(is_authenticated=True)
        def user_dashboard(request, w):
            # ... view logic for authenticated users ...

        # A custom permission check
        def is_editor(request):
            return request.user.is_staff

        @route(has_permissions=is_editor)
        def edit_article(request, w):
            # ... view logic for editors ...
        ```

        *   **Advanced Schemas: Alternate Views and Custom Structures:** While Byrdie's implicit schemas are great for getting started, you often need more control over how your API presents data. You might want different "views" of the same model for public vs. private APIs, or you might need to define a data structure that doesn't map directly to a model at all. Byrdie provides two powerful ways to handle this: `ModelSchema` for alternate model views, and `Schema` for completely custom data structures.

            *   **Alternate Model Schemas:** An `ModelSchema` allows you to define an alternate serialization schema for one of your existing models. It inherits the exposed fields and methods from the parent model by default, but you can precisely control what is included or excluded. This is perfect for creating variations of your API output without duplicating logic. For example, imagine you have a `Book` model, but you want a private version of the API that exposes a `private_function` and the full `text`, while hiding another field.

                ```python
                # In your app.py, alongside your models
                class PrivateBook(ModelSchema):
                    # The name of the model this schema is for
                    model = "Book"

                    # Explicitly expose fields or methods.
                    # This inherits from the model's own exposed items.
                    exposed = ["text", "private_function"]

                    # Hide fields that might otherwise be exposed.
                    hidden = ["other_field",]

                # You can then use this in your API view
                @route(api=True)
                def get_private_book_details(request, w) -> PrivateBook:
                    @w.do
                    def private_book():
                        return Book.objects.first()
                ```

                Key features of `ModelSchema`:
                *   **Inheritance:** It automatically inherits all fields and methods exposed on the base model.
                *   **Control:** Use `exposed` to add new fields/methods to the output and `hidden` to remove them.
                *   **Reusability:** Define it once and use it in any API view that returns a `Book`. You can even inherit from other `ModelSchema` classes to build up complex views.

            *   **Custom Schemas:** Sometimes your API needs to return data that doesn't match any of your models. It might be an aggregation of data from multiple sources, or a specific structure required by a frontend component. For these cases, you can use a `Schema`, which works just like a standard Pydantic or Ninja schema. Define a class that inherits from `byrdie.Schema` and add your fields with type hints. Byrdie will automatically use it to structure your API response.

                **Note on Instantiation:** Schemas are designed to be instantiated directly using their constructor. The constructor is flexible, accepting either keyword arguments (e.g., `MySchema(field=value)`) or a single positional dictionary (e.g., `MySchema({"field": "value"})`). The dictionary-based constructor is particularly useful as it supports automatic type coercion, converting string values from the dictionary into the appropriate field types defined in the schema. While returning a raw dictionary from a view that matches the schema fields is also supported, direct instantiation is the primary and recommended approach.

                ```python
                # In your app.py
                from byrdie import Schema
                from datetime import date

                class WeeklyReport(Schema):
                    start_date: date
                    end_date: date
                    new_users: int
                    notes_created: int
                    status: str = "OK"

                # Use it in an API view
                @route(api=True)
                def weekly_report(request, w) -> WeeklyReport:
                    # When using wove in an API, the result of the final task
                    # is automatically serialized using the view's schema.
                    @w.do
                    def report():
                        # The primary method is to return a schema instance.
                        return WeeklyReport(
                            start_date=date(2023, 1, 1),
                            end_date=date(2023, 1, 7),
                            new_users=15,
                            notes_created=120,
                            status="OK",
                        )
                ```

                This gives you full freedom to design your API outputs exactly as you need them, with the benefits of automatic validation and documentation.

            *   **Schema-Owned Routes:** For better organization, you can define routes directly on your `Schema` classes. This co-locates the data definition with the endpoint that serves it and allows Byrdie to infer the response type automatically.

                **Classmethod Routes for Collections:** If a route is decorated with `@classmethod`, Byrdie expects it to return a collection of items. The response will be automatically serialized as a `list` of the parent `Schema`.

                ```python
                class WeeklyReport(Schema):
                    # ... fields ...

                    @classmethod
                    @route(api=True)
                    def list_all(cls, request, w):
                        # Implicitly returns: list[WeeklyReport]
                        @w.do
                        def reports_data():
                            # ... logic to return a list of report instances ...
                            return [
                                WeeklyReport(start_date=date(2023, 1, 1), end_date=date(2023, 1, 7), new_users=15, notes_created=120, status="OK"),
                                WeeklyReport(start_date=date(2023, 1, 8), end_date=date(2023, 1, 14), new_users=22, notes_created=150, status="OK")
                            ]
                ```

                **Instance Method Routes for Single Items:** A regular method route takes `self` as its first argument. Byrdie will interpret its return type as the `Schema` class itself. This is suitable for detail views or actions on a single object, where Byrdie would provide the hydrated `self` object based on a path parameter.

                ```python
                class WeeklyReport(Schema):
                    # ... fields ...

                    # This route would likely correspond to a path like /api/weekly-report/{id}
                    @route(api=True)
                    def refresh(self, request, w):
                        # Implicitly returns: WeeklyReport
                        @w.do
                        def refreshed_data():
                            # ... can operate on self ...
                            self.status = "Refreshed"
                            return self
                ```

                **Overriding Return Types:** In either case, the implicit return type can be explicitly overridden with a standard Python type hint (e.g., `-> int`) if the route needs to return a different data structure.

                ```python
                class WeeklyReport(Schema):
                    # ... fields ...

                    @classmethod
                    @route(api=True)
                    def count(cls, request, w) -> int:
                        # Explicitly returns: int
                        @w.do
                        def total():
                            return 150
                ```

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
    *   **State:** Byrdie automatically initializes the component's data context by serializing the model's fields that are marked with `expose=True`. All exposed fields and methods are injected directly into the component's Alpine.js scope. Purely client-side state can be added using `x-data`.
    *   **Exposed Methods:** Use the `@expose` decorator on a method in your `Model` class to make it callable from the frontend. This function becomes available directly in the component's scope (e.g., `save()`).
    *   **Proxied API Routes:** API routes defined in Python with `@route(api=True)` are automatically exposed as functions on the global `byrdie` JavaScript object. For example, a Python route `def list_notes(...)` becomes `byrdie.list_notes()` in JavaScript. These functions handle the `fetch` request, JSON parsing, and model hydration internally, returning a promise that resolves with fully interactive Byrdie component instances. This creates a seamless connection between your backend and frontend code.
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
        <button @click="save(edited_text)">Save</button>
        <button @click="is_editing = false">Cancel</button>
    </div>

    <small>Created: {{ created_at|date:"M d, Y" }}</small>
</note>
```

#### Example: Working with Lists from an API

This example shows how to build a dynamic list of components by fetching data from an API.

**1. The API Endpoint: `app.py`**

We'll use the same `list_notes` API endpoint defined in the "Hello, Byrdie" application. It fetches all `Note` objects and returns them as a JSON array.

```python
# in app.py
@route(api=True)
def list_notes(request, w):
    return Note.objects.all()
```

**2. The Frontend Component: `templates/note_list_page.html`**

This component will fetch the notes from the API when it loads, hydrate them into interactive Byrdie components, and then display them. Each note in the list will have the same in-place editing functionality as the previous example.

```html
<!-- templates/note_list_page.html -->
<div x-data="{ notes: [] }" x-init="
    byrdie.list_notes().then(data => {
        notes = data;
    })
">
    <h1>My Notes (from API)</h1>

    <template x-for="note in notes" :key="note.id">
        <div class="note-container" style="border: 1px solid #ccc; padding: 1em; margin-bottom: 1em;">
            <!--
                Here, we are dynamically rendering the 'note' component.
                Since the 'note' object in our loop has been hydrated,
                it contains all the exposed data and methods.
                We can use x-data to pass the note object into the component's scope.
            -->
            <div x-data="note">
                <!-- This is the same in-place editing UI from the previous example -->
                <note x-data="{ is_editing: false, edited_text: text }">
                    <!-- Show this when not editing -->
                    <div x-show="!is_editing">
                        <p @dblclick="is_editing = true; edited_text = text">{{ text }}</p>
                    </div>

                    <!-- Show this when editing -->
                    <div x-show="is_editing" x-cloak>
                        <input type="text" x-model="edited_text">
                        <button @click="save(edited_text)">Save</button>
                        <button @click="is_editing = false">Cancel</button>
                    </div>

                    <small>Created: {{ new Date(created_at).toLocaleDateString() }}</small>
                </note>
            </div>
        </div>
    </template>
</div>
```

In this example:
- The main `div` calls `byrdie.list_notes()`. This function fetches the data, automatically hydrates the JSON response into interactive Byrdie components, and returns a promise that resolves with the final list of components.
- The `<template x-for="note in notes">` iterates through the hydrated notes.
- The `x-data="note"` on the inner `div` is the key part. It makes the properties of the current `note` object (like `text`, `created_at`, and the `save` method) available to all the elements inside it, including the `<note>` component.
- The `<note>` component itself can then use `save()` directly, because it was made available by the `x-data="note"` directive on its parent.
- We also use `new Date(created_at).toLocaleDateString()` to format the date, as the JSON value from the server is a string.

### F. Concurrent by Default with Wove

*   **Goal:** Make structured concurrency a core, effortless part of development. Byrdie embraces a concurrent-by-default philosophy, powered by `curvedinf/wove`.
*   **Mechanism:**
    *   **Wove by Default:** The `wove` integration is enabled for all routes by default, injecting a `w` object into every view function. This encourages developers to write non-blocking code from the start.
    *   **Task Naming:** Wove tasks should be named with nouns (e.g., `popular_authors`) instead of verbs (e.g., `get_popular_authors`). This reinforces the idea that a task represents its output data, not just its action.
    *   **Opt-out:** You can disable this behavior on a per-route basis by using `@route(wove=False)`.
    *   **Dependency Injection:** `wove` automatically builds a dependency graph of your tasks. A task can depend on the result of another by having a parameter with the same name as the dependency task.
    *   **Dynamic Mapping:** To run a task for each item in the result of another task, pass the name of the dependency task to the `@w.do()` decorator (e.g., `@w.do("popular_authors")`).
    *   **Automatic Context:** The view function does not need a `return` statement. Byrdie automatically executes the defined tasks and assembles the template context from their results.

#### Example: Dynamic Task Mapping

This example shows how `wove` can dynamically run tasks based on the output of a previous task.

1.  The `popular_authors` task runs first, fetching a list of authors.
2.  The `@w.do("popular_authors")` decorator on `author_stats` tells `wove` to run an instance of `author_stats` for *each author* in the result of the first task. All instances run concurrently.
3.  The `report` task then depends on the collected results of all `author_stats` runs.

```python
# app.py (a view using wove)
from byrdie import route
from .models import Author

@route() # wove is enabled by default
def author_report(request, w):
    # Task 1: A list of popular authors.
    @w.do
    def popular_authors() -> list[Author]:
        return Author.objects.filter(is_popular=True).limit(3)

    # Task 2: Stats for each author. This task is mapped over the
    # result of `popular_authors`. It will run concurrently for each author.
    @w.do("popular_authors")
    def author_stats(author: Author) -> dict:
        # The parameter `author` receives each item from the mapped list.
        return {
            "name": author.name,
            "book_count": author.books.count(),
            "first_book_year": author.books.order_by('year').first().year
        }

    # Task 3: A final report. This depends on the list of results
    # from all the `author_stats` task instances.
    @w.do
    def report(author_stats: list) -> dict:
        return {
            "report_title": "Popular Author Stats",
            "authors": author_stats # This is a list of dicts
        }
```

**Template: `templates/author_report.html`**

The template can access the results of any task by its function name. Here we use the final `report` result.

```html
<!-- templates/author_report.html -->
<h1>{{ report.report_title }}</h1>

<ul>
    {% for author_stats in report.authors %}
        <li>
            <strong>{{ author_stats.name }}</strong>
            ({{ author_stats.book_count }} books, first book in {{ author_stats.first_book_year }})
        </li>
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

## IV. Integrating with Existing Django Projects

While Byrdie is designed to create standalone applications with minimal setup, it can also be integrated into existing Django projects to leverage its features for specific parts of an application. This allows developers to use Byrdie's rapid development capabilities for new features within a larger, traditional Django application. Here's a conceptual guide:

1.  **Installation**: Add `byrdie` to your project's dependencies (e.g., in `requirements.txt`).
2.  **Create a Byrdie App**: Use the standard Django command to create a new app: `python manage.py startapp my_byrdie_app`.
3.  **Define Byrdie Components**: Inside this new app, create an `app.py` file. This file will be the home for your Byrdie-specific code, including `byrdie.Model` classes and views defined with the `@route` decorator. You can define your models and routes in this single file, as shown in the "Hello, Byrdie" example.
4.  **URL Integration**: To make the main Django project aware of your Byrdie routes, you'll need to point to them from your project's root `urls.py`. Byrdie will provide a utility function, let's call it `byrdie.get_urls()`, that discovers all `@route`-decorated views in a given module and returns a standard Django URL pattern list.

    ```python
    # project/urls.py
    from django.urls import path, include
    import my_byrdie_app.app

    urlpatterns = [
        # ... your other Django URL patterns
        path('my-new-feature/', include(my_byrdie_app.app.get_urls())),
    ]
    ```
5.  **Settings**: Finally, add your new app to the `INSTALLED_APPS` list in your project's `settings.py`:

    ```python
    # settings.py
    INSTALLED_APPS = [
        # ... other apps
        'my_byrdie_app',
    ]
    ```

This approach allows you to build a new feature using Byrdie's component-based, convention-driven style while keeping the rest of your Django project structure intact. It provides a flexible path for gradually adopting Byrdie or using it for specific, well-suited parts of a larger system.

## V. Technical Implementation Sketch

*   This section will be for brainstorming the "how." We'll think about the core `byrdie` application, the component rendering pipeline, and how we'll manage static assets.

## VI. Roadmap

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
