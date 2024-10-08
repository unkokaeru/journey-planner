#!/bin/bash

# Copied from https://github.com/alexfayers/image-to-excel/blob/main/scripts/release.sh
# This script is used to release a new version of the project.
# It will update the version in the actual package, create a new tag and push it to the remote repository.

# The version number is passed as an argument to the script.

echo "Releasing new version of journey_planner_python"

# Check if the git repo is dirty
if [[ -n $(git status --porcelain) ]]; then
    echo "The git repo is dirty. Please commit or stash your changes before releasing."
    exit 1
fi

# Check if the version number is passed as an argument

if [ -z "$1" ]
  then
    echo "No version number supplied."
    exit 1
fi

# Clear the current changelog - it gets regenerated fully on each release
echo '' > CHANGELOG.md

# Update the changelog
gitchangelog > CHANGELOG.md
git add CHANGELOG.md
git commit -m "Update CHANGELOG.md"

# Get the current version number
current_version=$(poetry version -s)

# Update the version number using poetry
poetry version "$1"

# Get the new version number
new_version=$(poetry version -s)

# Update the VERSION file
echo $new_version > source/journey_planner_python/VERSION
git add source/journey_planner_python/VERSION

# Update the version number in the git repo
git add .
git commit -m "Bump version: $current_version -> $new_version"

# Create a new tag and push it to the remote repository
git tag -a "v$new_version" -m "Release $new_version"

git push --follow-tags

# Build the package for PyPI
poetry build

# Publish the package to PyPI
poetry publish