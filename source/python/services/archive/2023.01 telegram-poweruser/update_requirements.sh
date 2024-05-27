poetry run pip list --format=freeze > requirements.txt

# remove editable installs and current library from requirements.txt
LINES_TO_DELETE="telegram-poweruser|lessmore|\[notice\]|Creating virtualenv"
mv requirements.txt requirements.txt.tmp
grep -vwE "($LINES_TO_DELETE)" requirements.txt.tmp > requirements.txt # todo: make a function, taken from here:   https://askubuntu.com/questions/354993/how-to-remove-lines-from-the-text-file-containing-specific-words-through-termina
rm requirements.txt.tmp