cd ${0%/*}

poetry run pip list --format=freeze > requirements.txt

# remove editable installs and current library from requirements.txt
LINES_TO_DELETE="second-sun|lessmore|\[notice\]"
mv requirements.txt requirements.txt.tmp
grep -vwE "($LINES_TO_DELETE)" requirements.txt.tmp > requirements.txt
rm requirements.txt.tmp