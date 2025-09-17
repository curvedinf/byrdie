# Getting Started with Byrdie

Byrdie is an opinionated Django wrapper that simplifies web development with Python. This guide walks you through creating your first Byrdie applications, starting with the basic "Hello, Byrdie" example and progressing to more advanced tutorials like building a simple blog and implementing authentication.

## Prerequisites

Before starting, ensure you have:

- Python 3.10 or higher installed.
- A virtual environment set up (recommended).

Install Byrdie and its dependencies:

```bash
pip install byrdie
```

Create a new directory for your project and navigate into it:

```bash
mkdir my_byrdie_app
cd my_byrdie_app
```

## Hello, Byrdie: Your First Application

The "Hello, Byrdie" example demonstrates the core concepts: models, routes, components, and the frontend bridge.

1. Create `app.py` with the following content:

```python
# app.py
from byrdie import Model, route, runserver, models

class Note(Model):
    text = models.CharField(max_length=255, expose=True)
    created_at = models.DateTimeField(auto_now_add=True, expose=True)
    components = ["card"]
    class Meta:
        ordering = ["-created_at"]

@route()
def index(request, w):
    if not Note.objects.exists():
        Note.objects.create(text="Hello, Byrdie!")
    @w.do
def notes():
        return Note.objects.all()
    return {'notes': notes}

if __name__ == "__main__":
    runserver()
```

2. Create the `components/note.html` template:

```html
<!-- components/note.html -->
<div class="note">
    <p>{{ note.text }}</p>
    <small>Created: {{ note.created_at|date:"M d, Y" }}</small>
</div>
```

3. Create `templates/index.html`:

```html
<!-- templates/index.html -->
{% block head %}
    <title>Hello, Byrdie</title>
{% endblock %}
<h1>Hello, Byrdie!</h1>
{% for note in notes %}
    <note />
{% endfor %}
```

4. Run the development server:

```bash
byrdie runserver
```

Visit `http://127.0.0.1:8000/` to see your first Byrdie app. You'll see a note rendered via the component system.

For the full "Hello, Byrdie" example, see the [examples/hello_world directory](../examples/hello_world/) (note: adjust path as per project structure).

## Building a Simple Blog Tutorial

This tutorial builds a basic blog with posts, using models, routes, Wove for concurrency, and components for rendering.

1. Create a new directory for the blog tutorial:

```bash
mkdir blog_tutorial
cd blog_tutorial
```

2. Define the `Post` model and routes in `app.py` (see the provided code in [examples/tutorials/blog/app.py](../examples/tutorials/blog/app.py) for a starting point).

   - The `Post` model uses `expose=True` for fields to enable API serialization.
   - The `index` route uses Wove (`@w.do`) to fetch posts concurrently.

3. Create the component template `components/post.html` (see [examples/tutorials/blog/components/post.html](../examples/tutorials/blog/components/post.html)) to render each post.

4. Create the page template `templates/index.html` (see [examples/tutorials/blog/templates/index.html](../examples/tutorials/blog/templates/index.html)) to list posts using `<post />` components.

5. Run migrations and the server:

```bash
byrdie makemigrations
byrdie migrate
byrdie runserver
```

6. Visit `http://127.0.0.1:8000/` to view the blog posts. Add CRUD operations by extending the routes (e.g., add `@route(api=True)` for API endpoints).

This tutorial covers models, components, routing, and basic concurrency. For the complete code, refer to the [blog tutorial directory](../examples/tutorials/blog/).

## Authentication and Sessions Tutorial

This tutorial adds user authentication with login/logout and protected routes.

1. In your project directory (or create a new one for this tutorial):

2. Define routes in `app.py` (see [examples/tutorials/auth/app.py](../examples/tutorials/auth/app.py)):

   - Use `@route(is_authenticated=True)` for protected views.
   - Implement a login view handling POST requests with Django's `authenticate` and `login`.
   - Add a "remember me" option via session expiry.

3. Create `templates/login.html` (see [examples/tutorials/auth/templates/login.html](../examples/tutorials/auth/templates/login.html)) for the login form, extending `base.html`.

4. Ensure `base.html` includes CSRF tokens and static files (as in the project templates).

5. Run migrations (if needed for auth models) and the server:

```bash
byrdie makemigrations
django migrate  # For auth tables
byrdie runserver
```

6. Test by visiting `/login/`, logging in (create a superuser if needed: `byrdie createsuperuser`), and accessing protected routes like `/profile/`.

This introduces route-level security and session management. For the full example, see the [auth tutorial directory](../examples/tutorials/auth/).

## Next Steps

- Explore core concepts in the [Core Concepts](../core-concepts/) section.
- Learn about integrations with [Wove](../integrations/wove/), [Django](../integrations/django/), and [Alpine.js](../integrations/alpinejs/).
- Check the [API reference](../api/) for detailed class and function docs.

For more tutorials, see [examples/tutorials/](../examples/tutorials/).
