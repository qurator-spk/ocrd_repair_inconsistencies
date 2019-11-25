# ocrd_repair_inconsistencies

Automatically fix order inconsistencies in regions, lines and words. Elements
are only fixed if reordering their children top-to-bottom/left-to-right fixes
the appropriately concatenated text of the children to match the parent's text.

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
