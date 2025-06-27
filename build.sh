#! /bin/bash

# Functions
function Ask {
  while true; do
    read -p "$* [y/N]: " yn
    case $yn in
      [Yy]*) return 0 ;;
      [Nn]*) return 1 ;;
      *) return 1 ;;
    esac
  done
}

function Build {
  echo "Deleting 'dist' directory..."
  rm ./dist -r
  echo "Building..."
  python3 -m build
}

function Publish {
  python3 -m twine upload --repository pypi dist/*
}

function Update {
  pip install --upgrade libjam
}

# Running
Build
Ask "Publish new version to PyPi?" && Publish &&
Ask "Update libjam?" && Update