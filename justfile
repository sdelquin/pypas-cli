dev:
    pip install -e .
build: clean
    python -m build
upload-test: build
    twine upload --repository testpypi dist/*
upload: build
    twine upload dist/*
clean:
    rm -fr build dist *egg* *cache*
open-pypi:
    open https://pypi.org/project/sendgrify/
