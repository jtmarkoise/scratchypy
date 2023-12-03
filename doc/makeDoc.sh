#!/bin/bash

mkdir -p api
cd .. && \
pydoctor \
    --project-name=ScratchyPy \
    --project-url=https://github.com/jtmarkoise/scratchypy/ \
    --make-html \
    --theme=readthedocs \
    --html-output=./doc/api \
    --project-base-dir="./scratchypy" \
    --docformat=epytext \
    ./scratchypy