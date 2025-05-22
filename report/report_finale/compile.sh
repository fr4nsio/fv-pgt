#!/usr/bin/env bash

pushd extra_code
python -m db
popd

pushd img/dbschema
mogrify -rotate 90 100_full.png
popd

pandoc \
    --from markdown \
    --to pdf \
    -o report.pdf \
    --highlight-style=tango \
    --verbose \
    report.md


#    --listings -H listings-setup.tex --toc -V geometry:"left=4cm, top=4cm, right=4cm, bottom=4cm" -V fontsize=12pt \
