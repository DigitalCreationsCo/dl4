#!/bin/bash

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install -r requirements.txt

echo "Environment setup complete. You can now run the application using ./scripts/run_flask.sh"
