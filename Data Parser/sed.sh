#!/bin/bash
find data/new -size -15k -type f # remove files under threshold
time { find data/new/* -type f -exec sed -s -i 's/\\"/"/g;s/\[\s*,/[/g;s/"\[/[/g;s/\\\+n//g;s/\,\+/,/g;s/]"/]/g' {} \; ; }

