# https://docs.astral.sh/uv/guides/package/#publishing-your-package

# Install pypas-cli in development mode
install:
    uv pip install .

# Clean temporary files
clean:
    rm -fr build dist *egg* *cache*

# Build project
build: clean
    uv build

# Upload to Test PyPI
upload-test: build
    uv publish -t `testpypi-token` --publish-url "https://test.pypi.org/legacy/"

# Upload to PyPI
upload: build
    uv publish -t `pypi-token`

# Open project url at Test PyPI
open-testpypi:
    open https://test.pypi.org/project/pypas-cli/

# Open project url at PyPI
open-pypi:
    open https://pypi.org/project/pypas-cli/

# Test pypas command
test args:
    uv run --with pypas-cli --no-project --refresh-package pypas-cli -- {{args}}
