#!/bin/bash

# Requires inkscape ( brew install caskformula/caskformula/inkscape )
# Requires optipng

BG_COLOR="#FFF"
SINGLE_FILEPATH=''
DPI=512

if [[ ! -z "$1" && "$1" != "" && "$1" != "-a" ]]; then
    echo "Using $1 for SINGLE_FILEPATH"
    SINGLE_FILEPATH="$1"
fi

if [[ ! -z "$2" && "$2" != ""  ]]; then
    echo "Using $2 for BG_COLOR"
    BG_COLOR="$2"
fi

run_single()
{
    inkscape -z -f "${SINGLE_FILEPATH}" -e "${SINGLE_FILEPATH%svg}png" -b "${BG_COLOR}" -d ${DPI}
    optipng "${SINGLE_FILEPATH%svg}png" -o1
}

run_multiple()
{
cd output/
for file in *.svg
do
    inkscape -z -f "${file}" -e "${file%svg}png" -b "${BG_COLOR}" -d ${DPI}
    optipng "${file%svg}png" -o1
done
cd ..
}

if [[ ! -d "./output/" ]]; then
    echo "No output directory, we're done here"
    exit 0
fi

# Pass -a to apply the bg color change to all
if [[ ! -z "$1" && "$1" != "-a"  ]]; then
    echo "Converting $1"
    run_single
else
    run_multiple
fi