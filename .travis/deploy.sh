#!/bin/bash

set -e

if [ "$TRAVIS_OS_NAME" = "osx" ]; then
    eval "$(pyenv init -)"
    pyenv activate Windmapper
fi

if [ "$test_conda" = "1" ]; then exit 0 ; fi

pip install twine
pip install conan
pip install scikit-build==0.10.0
pip install ninja
pip install wheel

if [ "$TRAVIS_OS_NAME" = "osx" ]; then
  python setup.py sdist 
else
  python setup.py sdist 
fi
twine upload  --skip-existing dist/*