#!/bin/bash

python svg.py -f txt/lyme_savvy.txt && sh convert.sh output/lyme_savvy.svg "#537E63"
python svg_split.py -f txt/zen.txt && sh convert.sh output/zen.svg "#152C35"
python svg_split.py -f txt/wizard_of_oz.txt && sh convert.sh output/wizard_of_oz.svg "#000"
python svg_split.py -f txt/making_a_pearl.txt && sh convert.sh output/making_a_pearl.svg "#000"
python svg_split.py -f txt/frankenstein.txt && sh convert.sh output/frankenstein.svg "#00005A"
python svg_split.py -f txt/bible.txt && sh convert.sh output/bible.svg "#00005A"

python svg_split.py -f txt/cuckoos_egg.txt && sh convert.sh output/cuckoos_egg.svg "#000"


