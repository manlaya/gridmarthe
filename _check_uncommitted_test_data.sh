#!/bin/bash
# This script inspect the tests directory and check if any file used in tests
# is not committed.
# If no output is produced, then it's all good.

# This can be a pre-commit hook.
# To install it, run:
# [ -f .git/hooks/pre-commit ] && cat ./_check_uncommitted_test_data.sh >> .git/hooks/pre-commit || cp _check_uncommitted_test_data.sh .git/hooks/pre-commit

status=0

if [ ! -d tests/ ]; then
    echo 'No tests directory found, please run at repository root'
    exit 1
fi

# https://stackoverflow.com/questions/466764/git-command-to-show-which-specific-files-are-ignored-by-gitignore
UNTRACKED=($(git check-ignore -v -- tests/data/* | awk '{print $2}'))
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
