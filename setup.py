from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="byrdie",
    version="0.1.0",
    author="Byrdie Team",
    author_email="byrdie@example.com",
    description="Byrdie is an opinionated Django wrapper designed for simplicity, productivity, and modern web development practices.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Django",
        "Framework :: Django :: 5.0",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=[
        "Django>=5.0",
        "wove",
        "pydantic",
        "django-ninja",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-django",
        ],
        "test": [
            "pytest",
            "pytest-django",
        ],
    },
    entry_points={
        "console_scripts": [
            "byrdie=byrdie.cli:main",
        ],
    },
)
