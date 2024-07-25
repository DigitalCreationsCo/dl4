#!/bin/bash

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Run the Flask application and log output
flask run &> flask.log &
