# Byrdie Automated Documentation Plan

## 1. Objective

This document outlines a plan to create a comprehensive, automated, and beautiful documentation system for the Byrdie framework. The goal is to produce a living reference that serves two primary purposes:

1.  **Self-documenting code:** Provide an API reference that is automatically generated from the Byrdie source code, ensuring it is always up-to-date.
2.  **Integrated Project Reference:** Offer clear, narrative documentation that explains Byrdie's core concepts and how it integrates with its constituent technologies: Django, Wove, and Alpine.js.

The final output will be a modern, easily navigable, and aesthetically pleasing HTML website.

## 2. Recommended Tooling

*   **Documentation Generator:** **Sphinx**. It is the standard for Python projects and offers unparalleled flexibility and power.
    *   **Why Sphinx?** It has robust support for automatically generating documentation from source code, a vast ecosystem of extensions, and mature support for theming and customization.
*   **Markup Language:** **MyST (Markedly Structured Text)**. We will use the `myst-parser` extension for Sphinx.
    *   **Why MyST?** It allows us to write documentation in Markdown, which is simpler and more widely known than reStructuredText. It is also a superset of Markdown, so it can be extended to support Sphinx's powerful directives.
*   **Theme:** **Furo**.
    *   **Why Furo?** It is a modern, clean, and highly customizable Sphinx theme that is optimized for readability and navigation.

## 3. Documentation Structure

The documentation will be organized into the following top-level sections:

```
docs/
├── source/
│   ├── _static/              # Custom CSS and images
│   ├── _templates/           # Template overrides
│   ├── getting-started.md
│   ├── core-concepts/
│   │   ├── routing.md
│   │   ├── models-and-components.md
│   │   ├── templating.md
│   │   └── frontend-bridge.md
│   ├── integrations/
│   │   ├── wove.md           # Will directly include content from wove.md
│   │   ├── django.md
│   │   └── alpinejs.md
│   └── api/
│       ├── byrdie.md
│       └── byrdie.routing.md # Auto-generated API docs
│   ├── conf.py               # Sphinx configuration
│   └── index.md              # The main landing page
└── Makefile                  # To automate the build
```

## 4. Automation and Content Strategy

### 4.1. Byrdie's Core Concepts (Narrative Documentation)

This section will be manually written in Markdown. It will serve as the primary guide for learning Byrdie. The content will be adapted from the existing `plan.md` and `project-structure.md` documents.

*   **`getting-started.md`**: A tutorial that walks a new user through building the "Hello, Byrdie" application.
*   **`core-concepts/*.md`**: A series of guides that dive deep into Byrdie's main features (routing, model-component architecture, template engine, frontend bridge).

### 4.2. Byrdie's API (Self-documenting Code)

This section will be automatically generated from the docstrings in the Byrdie source code.

*   **Implementation:** We will use Sphinx's `autodoc` extension. In the `api/*.md` files, we will use `autodoc` directives to point to the Byrdie Python modules (e.g., `byrdie.routing`).
*   **Requirement:** This requires that the Byrdie source code follows good practices for writing docstrings (e.g., using Google-style or NumPy-style docstrings).

### 4.3. Constituent Projects (Integrated Reference)

This section will explain how Byrdie builds upon other technologies.

*   **Wove:** We will use `myst-parser`'s `include` directive to directly pull in the content from the existing `wove.md` file. This ensures that the Wove documentation is a single source of truth.
*   **Django:** We will not replicate Django's documentation. Instead, `django.md` will be a guide that explains the relationship between Byrdie and Django. It will cover:
    *   How Byrdie simplifies Django's concepts (e.g., settings, apps).
    *   How to use existing Django libraries within a Byrdie project.
    *   Links to the official Django documentation for further reading.
*   **Alpine.js:** Similar to the Django approach, `alpinejs.md` will explain how Byrdie's Frontend Bridge leverages Alpine.js. It will provide examples and link to the official Alpine.js documentation for details on Alpine's directives and syntax.

## 5. Build and Deployment Process

1.  **Setup:**
    *   Create the `docs/` directory and a `requirements-docs.txt` file with the necessary dependencies (`sphinx`, `furo`, `myst-parser`).
    *   Run `sphinx-quickstart` to generate the initial configuration.
    *   Modify `docs/source/conf.py` to enable the required extensions (`autodoc`, `myst_parser`) and set the theme to `furo`.

2.  **Build:**
    *   A `Makefile` will be created in the `docs/` directory with commands to simplify the build process.
        *   `make html`: To build the HTML documentation.
        *   `make clean`: To remove old build artifacts.

3.  **Deployment (CI/CD):**
    *   The build process can be integrated into a CI/CD pipeline (e.g., GitHub Actions).
    *   On every push to the `main` branch, the CI/CD pipeline will:
        1.  Install the documentation dependencies.
        2.  Run `make html`.
        3.  Deploy the generated HTML files (in `docs/build/html`) to a static hosting service like GitHub Pages, Netlify, or Vercel.

## 6. Next Steps

1.  Initialize the `docs` directory and Sphinx configuration.
2.  Create the initial Markdown files for the narrative documentation.
3.  Configure `autodoc` and set up the initial API documentation pages.
4.  Integrate the `wove.md` file.
5.  Write the initial content for the Django and Alpine.js integration guides.
6.  Set up the CI/CD pipeline for automated deployment.
