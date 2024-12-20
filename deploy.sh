#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Install gunicorn if not already installed
pip install gunicorn

# Run with gunicorn
gunicorn \
    --workers 4 \
    --bind 0.0.0.0:8081 \
    --timeout 120 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --log-level info \
    main:app
