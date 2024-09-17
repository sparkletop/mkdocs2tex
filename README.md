# mkdocs2tex

Converts a tree of MkDocs .md files to LaTeX format, with table of contents, list of figures, list of tables and properly placed and dimensioned images.

Reads the whole documentation contents, adjusts it, converts it into LaTeX format using pandoc, adjusts that LaTeX content, writes the result to an `output.tex` file.

## Requirements

 * python3
 * pandoc

## Installation

 * Clone this repo
 * Run this to install necessary python packages: `pip install -r requirements.txt`

## Usage

`python3 ./mkdocs2tex.py -i /path/to/mkdocs.yml`

### Options

```
python3 ./mkdocs2tex.py -h

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        source MkDocs .yml configuration file
  -o OUTPUT, --output OUTPUT
                        generated .tex file name
  -t TMP, --tmp TMP     directory for temporary files during conversion
```

Caveat: use absolute paths

## Build PDF from generated LaTeX

### Requirements

 * texlive
 * texlive-latex-extra
 * texlive-bibtex-extra
 * texlive-font-utils
 * lmodern
 * latexmk

### Build PDF

`latexmk -f -pdf -interaction=nonstopmode output.tex`

## Contributors

 * [@DDorch](https://github.com/DDorch) (original work)
