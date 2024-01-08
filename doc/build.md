# Build Notes

## Release checklist
1. Update version in __version__.py
1. Update version in pyproject.toml
1. Update links/images in README.md to point to a commit version.

## Build the package

1. Build with `python -m build`
1. Clear out the dist/ directory.
1. Upload to PyPI with `twine upload dist/*`