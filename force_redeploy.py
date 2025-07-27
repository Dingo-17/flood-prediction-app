#!/usr/bin/env python3
"""
Force redeploy trigger for Render.com
This file is updated to trigger a new deployment
"""

import datetime
import os

# Get current timestamp
timestamp = datetime.datetime.now().isoformat()

print(f"Force redeploy triggered at: {timestamp}")
print("Deployment configuration:")
print("- Build command: pip install -r requirements-production.txt")
print("- Start command: python app.py")
print("- Environment: production")
print("- Port: 10000")

# Check if required files exist
required_files = [
    'app.py',
    'requirements-production.txt',
    'render.yaml'
]

for file in required_files:
    if os.path.exists(file):
        print(f"✓ {file} exists")
    else:
        print(f"✗ {file} missing")

print("\nIf deployment fails, check:")
print("1. GitHub repository has all files")
print("2. Render.com build command is: pip install -r requirements-production.txt")
print("3. Render.com start command is: python app.py")
print("4. Environment variables are set correctly")
