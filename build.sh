#! /bin/bash

echo "Removing 'dist' directory..."
rm ./dist -r
python3 -m build

# Publish command:
# python3 -m twine upload --repository pypi dist/*
