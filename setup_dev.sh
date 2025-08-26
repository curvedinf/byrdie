#!/bin/bash
set -e

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Installing constituent projects..."
PROJECTS_FILE="gitdepends.txt"
PROJECTS_DIR="constituent_projects"

if [ -f "$PROJECTS_FILE" ]; then
    mkdir -p "$PROJECTS_DIR"
    echo "--> Created directory for constituent projects at $PROJECTS_DIR"

    # Read gitdepends.txt, ignoring comments and empty lines
    grep -v '^#' "$PROJECTS_FILE" | grep -v '^$' | while IFS=, read -r name url version; do
        echo "--- Processing project: $name ---"
        PROJECT_PATH="$PROJECTS_DIR/$name"

        echo "Cloning $url into $PROJECT_PATH..."
        git clone "$url" "$PROJECT_PATH"

        cd "$PROJECT_PATH"

        echo "Checking out version/branch: $version..."
        git checkout "$version"

        echo "Installing project $name in editable mode..."
        pip install -e .

        cd ../..

        echo "--- Finished processing project: $name ---"
    done
else
    echo "--> No gitdepends.txt file found, skipping constituent project installation."
fi

echo "Setup complete. To activate the virtual environment, run: source venv/bin/activate"
