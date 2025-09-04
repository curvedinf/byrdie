# Django Integration

Byrdie is built on top of Django and is designed to be fully interoperable with the Django ecosystem. While Byrdie provides a simplified, convention-over-configuration approach to web development, it still leverages the power and stability of Django under the hood.

## How Byrdie Simplifies Django

Byrdie simplifies several of Django's core concepts to reduce boilerplate and make development faster and more intuitive.

### Projects and Apps

In Django, a "project" is a container for configuration and one or more "apps". This creates a nested directory structure that can be confusing for beginners. Byrdie removes the "project" layer, making the application itself the top-level container.

A "Byrdie app" is simply a Python module or package where you organize related code. There is no formal "app" registration required in a settings file. As long as a module is imported by your main `app.py`, Byrdie will discover its routes, models, and other components.

### Settings

Byrdie can be configured using a standard Django `settings.py` file. If a `settings.py` file is found in the same directory as your `app.py`, Byrdie will automatically use it. This allows you to use familiar Django settings like `DATABASES`, `INSTALLED_APPS`, and `MIDDLEWARE`.

## Using Django Libraries

You can use existing Django libraries and packages in your Byrdie project. Simply install them and add them to the `INSTALLED_APPS` list in your `settings.py` file.

## Further Reading

For more information on Django, please refer to the official [Django documentation](https://docs.djangoproject.com/en/stable/).
