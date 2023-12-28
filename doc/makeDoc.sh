#!/bin/bash

mkdir -p apidocs
pydoctor \
    --project-name=ScratchyPy \
    --project-url=https://github.com/jtmarkoise/scratchypy/ \
    --make-html \
    --theme=readthedocs \
    --html-output=./apidocs \
    --project-base-dir="$(pwd)" \
    --docformat=epytext \
    ./scratchypy
    
# ignore errors until later
true