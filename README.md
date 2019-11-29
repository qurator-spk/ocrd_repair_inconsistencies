# ocrd_repair_inconsistencies

    Automatically re-order lines, words and glyphs to become textually consistent with their parents.

## Introduction

PAGE-XML elements with textual annotation are re-ordered by their centroid coordinates
iff such re-ordering fixes the inconsistency between their appropriately concatenated
`TextEquiv` texts with their parent's `TextEquiv` text.

If `TextEquiv` is missing, skip the respective elements.

Where available, respect the annotated visual order:
- For regions vs lines, sort in `top-to-bottom` fashion, unless another `textLineOrder` is annotated.  
  (Both `left-to-right` and `right-to-left` will be skipped currently.)
- For lines vs words and words vs glyphs, sort in `left-to-right` fashion, unless another `readingDirection` is annotated.  
  (Both `top-to-bottom` and `bottom-to-top` will be skipped currently.)

This processor does not affect `ReadingOrder` between regions, just the order of the XML elements
below the region level, and only if not contradicting the annotated `textLineOrder`/`readingDirection`.

We wrote this as a one-shot script to fix some files. Use with caution.

## Installation

(In your venv, run:)

```sh
make deps     # or pip install -r requirements.txt
make install  # or pip install .
```

## Usage

Offers the following user interfaces:

### [OCR-D processor](https://ocr-d.github.io/cli) CLI `ocrd-repair-inconsistencies`

To be used with [PageXML](https://github.com/PRImA-Research-Lab/PAGE-XML)
documents in an [OCR-D](https://ocr-d.github.io) annotation workflow.

### Example

Use the following script to repair `OCR-D-GT-PAGE` annotation in workspaces,
and then replace it with the output on success:

~~~sh
#!/bin/bash
set -e

tmp_fg=FIXED_$RANDOM

ocrd-repair-inconsistencies -I OCR-D-GT-PAGE -O $tmp_fg

for f in "$tmp_fg"/*; do
  g="OCR-D-GT-PAGE/OCR-D-GT-PAGE_${f#${tmp_fg}/${tmp_fg}_}"
  cp "$f" "$g"
done

ocrd workspace remove-group -rf $tmp_fg
rmdir $tmp_fg
~~~
