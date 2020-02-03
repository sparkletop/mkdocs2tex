# mkdocs2tex

Converts a bunch of MkDocs .md files to LaTeX format.

Converts the whole documentation contents into an `output.tex` file, that can be
included in a LaTeX template for subsequent PDF compilation.

## Requirements

 * python3
 * pandoc

## Usage

`python3 ./mkdocs2tex.py`

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

Note that if you use `--output` option, you'll have to change the LaTeX template `\input{}` command.

## Build PDF from generated LaTeX

An example `template.tex` is given, that `\input{}s` the generated `output.tex`. Take it as an example to build your own template.

### Requirements

 * texlive
 * texlive-latex-extra
 * texlive-bibtex-extra
 * texlive-font-utils
 * latexmk

### Build PDF

`latexmk -f -pdf -interaction=nonstopmode template.tex`

## Contributors

 * [@DDorch](https://github.com/DDorch) (original work)
