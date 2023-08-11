poetry run pip list --format=freeze > requirements.txt

# remove editable installs and current library from requirements.txt
LINES_TO_DELETE="discord-to-telegram-forwarder|lessmore|\[notice\]"
mv requirements.txt requirements.txt.tmp
grep -vwE "($LINES_TO_DELETE)" requirements.txt.tmp > requirements.txt
rm requirements.txt.tmp