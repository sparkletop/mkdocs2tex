#! /usr/bin/env python3

import os
import argparse
import yaml
import re
import shutil
import sys

baseDir = os.getcwd();

# Default configuration
inputFile = os.path.join(baseDir, 'mkdocs.yml')
outputFile = os.path.join(baseDir, 'output.tex')
buildDir = os.path.join(baseDir, 'tmp')

# Other globals
mergedTexFile = ''

# Reads an MkDocs configuration file
def readConfig(sYAML):
    f = open(sYAML, 'r')
    with f:
        try:
            dMkdocsYaml = yaml.load(f, Loader=yaml.SafeLoader)
        except yaml.YAMLError as e:
            sys.exit("ERROR on YAML loading {}: {}".format(sYAML, str(e)))
    return dMkdocsYaml


def getMdHeader(title, level):
    return "#" * level + " " + title + "\n"


def shiftMdHeaders(mdContent, level):
    if level == 0:
        return mdContent

    lMd = mdContent.splitlines()
    for i, item in enumerate(lMd):
        if len(item) > 0 :
            if item[0] == "#":
                lMd[i] = ("#" * level) + item
    return "\n".join(lMd)


# Build a navigation tree in alphanumeric order based on directory tree and .md files
def buildNavTree(docs_dir):
    nav = []
    
    # Add .md files in current directory
    files = [f for f in os.listdir(docs_dir) if os.path.isfile(os.path.join(docs_dir, f)) and f.endswith(".md")]
    files.sort()
    nav.extend(files)

    # Recurse into subdirectories
    dirs = [d for d in os.listdir(docs_dir) if os.path.isdir(os.path.join(docs_dir, d))]
    dirs.sort()
    for dir in dirs:
        sub_nav = buildNavTree(os.path.join(docs_dir, dir))

        # Prepend subdirectory to filename
        for i, element in enumerate(sub_nav):
            if type(element) is str:
                sub_nav[i] = os.path.join(dir, element)
        
        if sub_nav: # only add non-empty subdirectories
            nav.append({dir: sub_nav})

    return nav


# Browses MkDocs configuration file and merges .md files
def exploreAndMerge(docs_dir, nav, output = '', level = 0):
    """
    @param docs_dir path to the mkdocs content files
    @param nav dictionnary with the structure to explore
    @param output merged markdown files content
    """

    # No nav specified in MkDocs yaml, build one from contents of docs_dir
    if nav is None:
        nav = buildNavTree(docs_dir)

    # Navigate file/directory tree
    if type(nav) is str:
        nav = [nav]
    for d in nav:
        if type(d) is str:
            filepath = os.path.join(docs_dir, d)
            f = open(filepath, 'r')
            path = os.path.dirname(filepath)
            s = f.read() + "\n"
            # Modification of image and links paths
            s = re.sub(r'(\!\[.+\]\()(.+)(\))', r'\1'+path+r'/\2\3', s)
            s = re.sub(r'(\\\()(.+?)(\\\))', r'$\2$', s)
            s = shiftMdHeaders(s, level)
            output += "\n" + s

        elif type(d) is dict:
            level += 1
            for key, value in d.items():
                if type(value) is list:
                    output += "\n" + getMdHeader(key, level) + "\n"
                    output = exploreAndMerge(docs_dir, value, output, level)
                else:
                    # do not dig level when sub-chapter has only one entry (alias)
                    output = exploreAndMerge(docs_dir, value, output, level-1)
            level -= 1
    return output


# Creates a filePath.tex LaTeX contents file based on filePath.md
def convertMdToTex(filePath):
    # Convert .md to .tex
    os.system(
        'pandoc {} -f markdown -t latex -s -o {}'.format(filePath, mergedTexFile)
    )
    # Adjust generated content
    ls = ''
    with open(mergedTexFile, 'r') as f:
        for line in f:
            # ls.append(line)
            l = line
            # adjust images max width/height
            l = l.replace('\\includegraphics', '\\includegraphics[max size={\\textwidth}{0.9\\textheight}]')
            # force figures placement
            l = l.replace('\\begin{figure}', '\\begin{figure}[h!]')
            ls = ls + l

    # Inject custom contents
    ls = ls.replace('\\author{}', '\\usepackage[section]{placeins}\n\n\\author{}')
    ls = ls.replace('\\begin{document}', '\\begin{document}\n\n\\tableofcontents')
    ls = ls.replace('\\end{document}', '\\listoffigures\n\\listoftables\n\n\\end{document}')


    # Save merged LaTeX file
    with open(mergedTexFile, 'w') as f:
        f.writelines(ls)


if __name__ == '__main__':

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="source MkDocs .yml configuration file")
    parser.add_argument("-o", "--output", help="generated .tex file name")
    parser.add_argument("-t", "--tmp", help="directory for temporary files during conversion")
    args = parser.parse_args()
    if args.input:
        inputFile = args.input
    if args.output:
        outputFile = args.output
    if args.tmp:
        buildDir = args.tmp

    # Prepare temp dir
    os.makedirs(buildDir, exist_ok=True)
    mergedTexFile = os.path.join(buildDir, 'merged.tex')

    # Read config
    dMkdocsYaml = readConfig(inputFile)

    # Merge MarkDown into string
    docsDir = dMkdocsYaml.get('docs_dir') or 'docs'
    if not os.path.isabs(docsDir):
        docsDir = os.path.join(os.path.dirname(inputFile), docsDir)
    
    s = exploreAndMerge(docsDir, dMkdocsYaml.get('nav'))

    # Remove internal links
    s = re.sub(r'\[([^/]+)\]\([^ ]+\.md\)', r'\1', s)

    # Save the merged .md file
    mergedDocOutputPath = os.path.join(buildDir, "merged.md")
    with open(mergedDocOutputPath, 'w') as f:
        f.writelines(s)

    # Convert to tex format
    convertMdToTex(mergedDocOutputPath)

    # Copy merged .tex file to output directory
    shutil.copyfile(mergedTexFile, outputFile)

    # Clean build dir
    # shutil.rmtree(buildDir)
