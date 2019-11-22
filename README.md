# ocrd_repair_inconsistencies

Automatically fix order inconsistencies in regions, lines and words. Elements
are only fixed if reordering their children top-to-bottom/left-to-right fixes
the appropriately concatenated text of the children to match the parent's text.

We wrote this as a one-shot script to fix some files. Use with caution.
