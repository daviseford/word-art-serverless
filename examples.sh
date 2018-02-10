#!/bin/bash

python svg.py -f txt/bible.txt -c grey && sh convert.sh output/bible.svg
python svg.py -f txt/purple_cow.txt -c "#d40adb" && sh convert.sh output/purple_cow.svg
python svg.py -f txt/romance_of_lust.txt -c "#e51919" && sh convert.sh output/romance_of_lust.svg
python svg.py -f txt/the_republic.txt && sh convert.sh output/the_republic.svg
python svg.py -f txt/wizard_of_oz.txt -c yellow && sh convert.sh output/wizard_of_oz.svg "#000" && convert output/wizard_of_oz.png -rotate 270 output/wizard_of_oz.png;
python svg.py -f txt/ulysses.txt -c green && sh convert.sh output/ulysses.svg white
python svg.py -f txt/frankenstein.txt -c green && sh convert.sh output/frankenstein.svg black
python svg.py -f txt/zen.txt -c "#DF169E" && sh convert.sh output/zen.svg "#00D2D9" && convert output/zen.png -rotate 90 output/zen.png;


