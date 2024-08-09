#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Define variables
APP_DIR="."
VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"
STATIC_DIR="static"
FLASK_APP="app"  # Replace with your actual Flask app name

echo "Starting build process..."

# Activate virtual environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Install or upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install production dependencies
echo "Installing production dependencies..."
pip install -r $REQUIREMENTS_FILE

# Install Gunicorn
echo "Installing Gunicorn..."
pip install gunicorn

# Set Flask environment to production
export FLASK_ENV=production

# Run database migrations (if applicable)
if [ -d "migrations" ]; then
    echo "Running database migrations..."
    flask db upgrade
fi

# Collect static files (if applicable)
if [ -d "$STATIC_DIR" ]; then
    echo "Collecting static files..."
    # You might need to implement your own static file collection logic here
    # For example: python manage.py collectstatic (if using Django-style static collection)
fi

# Run tests
# echo "Running tests..."
# python -m pytest

# Compile Python bytecode
echo "Compiling Python bytecode..."
python -m compileall .

# Create or update requirements.txt
echo "Updating requirements.txt..."
pip freeze > $REQUIREMENTS_FILE

# Create a production-ready wsgi.py file
echo "Creating wsgi.py..."
cat > wsgi.py << EOL
from $FLASK_APP import app

if __name__ == "__main__":
    app.run()
EOL

# Create a Procfile for Gunicorn
echo "Creating Procfile..."
echo "web: gunicorn wsgi:app" > Procfile

echo "Build process completed successfully!"

# Deactivate virtual environment
deactivate

echo "Ready for deployment!"