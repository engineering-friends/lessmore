poetry run pip list --format=freeze > requirements.txt

# remove editable installs, current library and pip comments from requirements.txt
LINES_TO_DELETE="deeplay|monorepo-tooling|\[notice\]"
mv requirements.txt requirements.txt.tmp
grep -vwE "($LINES_TO_DELETE)" requirements.txt.tmp > requirements.txt # todo later: make a function, taken from here:   https://askubuntu.com/questions/354993/how-to-remove-lines-from-the-text-file-containing-specific-words-through-termina
rm requirements.txt.tmp