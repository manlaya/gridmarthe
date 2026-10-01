#!/bin/bash
# This script inspect the tests directory and check if any file used in tests
# is not committed.
# If no output is produced, then it's all good.

status=0

# Ensure we are in the repo root
cd "$(git rev-parse --show-toplevel)" || exit 1

if [ ! -d tests/ ]; then
    echo 'No tests directory found, please run at repository root'
    exit 1
fi

# https://stackoverflow.com/questions/466764/git-command-to-show-which-specific-files-are-ignored-by-gitignore
IGNORED=($(git check-ignore -v -- tests/data/* | awk '{print $2}'))
UNTRACKED=($(git status -s | grep '^??' | awk '{print $2}'))
UNTRACKED=("${IGNORED[@]}" "${UNTRACKED[@]}")
for FTEST in "${UNTRACKED[@]}";do
    if grep -q $FTEST tests/*.*; then
        echo "File used in tests but uncommitted: $FTEST"
        status=1
    fi
done

if [ $status -eq 1 ]; then
    echo "Please commit the files above"
    exit 1
fi

exit 0
