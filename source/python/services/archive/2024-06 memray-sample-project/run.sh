# - Go to current directory



# - Remove old memray files if exist

rm memray_report.bin
rm flamegraph.html

# - Run memray

poetry run memray flamegraph memray_report.bin --force --output flamegraph.html

# - Open flamegraph in browser

xdg-open flamegraph.html