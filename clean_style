#!/usr/bin/env bash

# Convert "<hr/>" to "---"
perl -pe 's|"<hr\/>"|"---"|' -i *json

# Collapse multiple, sequential `"---",` to one.
perl -0pe 's|\n(\s+"---",\n){2,}|\n      "---",\n|' -i *json

# Collapse ending double hr's to one.
perl -0pe 's|\n(\s+"---",\n)+(\s+"---")\n|\n\2\n|' -i *json

# Convert "<br/>" to ""
perl -pe 's|"<br\/>"|""|' -i *json

# Remove <reward> and <task> widgets from descriptions
perl -pe 's/^\s+"<[reward|task].*",?//' -i *json

# Remove trailing comma in destription json list
perl -0pe 's|",\n(\s+\],)|"\n\1|' -i *json

# trim empty lines
sed -i '/^$/d' *json

