# https://docs.astral.sh/uv/guides/package/#publishing-your-package

# Install pypas-cli in development (editing) mode
install:
    #!/usr/bin/env bash
    uv pip install -e .
    echo
    echo "✔ Use 'uv run pypas' or alias 'pypas-dev' to run the CLI tool."

# Clean temporary files
clean:
    rm -fr build dist *egg* *cache*

# Build project
build: clean
    uv build

# Upload to Test PyPI
upload-test: build
    uv publish -t $TESTPYPI_TOKEN --publish-url "https://test.pypi.org/legacy/"

# Upload to PyPI
upload: build
    uv publish -t $PYPI_TOKEN

# Open project url at Test PyPI
open-testpypi:
    open https://test.pypi.org/project/pypas-cli/

# Open project url at PyPI
open-pypi:
    open https://pypi.org/project/pypas-cli/

# Open iPython shell
sh:
    uv run ipython

# Bump version: component = [major, minor, patch]
bump component:
    uv version --bump {{component}}
