# ocrd_repair_inconsistencies

Automatically re-order lines, words and glyphs to become textually consistent with their parents.

PAGE-XML elements with textual annotation are re-ordered by their centroid coordinates
in top-to-bottom/left-to-right fashion iff such re-ordering fixes the inconsistency
between their appropriately concatenated `TextEquiv` texts with their parent's `TextEquiv` text.

This processor does not affect `ReadingOrder` between regions, just the order of the XML elements below the region level, and only if not contradicting the annotated `textLineOrder`/`readingDirection`.

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
