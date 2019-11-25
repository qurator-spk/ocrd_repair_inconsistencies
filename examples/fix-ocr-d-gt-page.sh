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
