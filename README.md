# ocrd_repair_inconsistencies

Automatically fix PAGE-XML order inconsistencies in regions, lines and words.
Children elements are only reordered if reordering by coordinates
top-to-bottom/left-to-right fixes the appropriately concatenated `TextEquiv`
texts of the children to match the parent's `TextEquiv` text. This processor
does not change reading order, just the order of the XML elements in the file.

We wrote this as a one-shot script to fix some files. Use with caution.


## Example usage

For example, use this fix script:
~~~sh
#!/bin/bash
set -e

tmp_fg=FIXED_$RANDOM

ocrd_repair_inconsistencies -I OCR-D-GT-PAGE -O $tmp_fg

for f in "$tmp_fg"/*; do
  g="OCR-D-GT-PAGE/OCR-D-GT-PAGE_${f#${tmp_fg}/${tmp_fg}_}"
  cp "$f" "$g"
done

ocrd workspace remove-group -rf $tmp_fg
rmdir $tmp_fg
~~~
