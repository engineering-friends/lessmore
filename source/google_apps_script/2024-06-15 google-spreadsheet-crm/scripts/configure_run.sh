# https://github.com/google/clasp/blob/master/docs/run.md

cd ${0%/*}
cd ../source

# some extracts from the docs
# Create project and app from creator of the page: https://cloud.google.com/resource-manager/docs/creating-managing-projects
# Enable Google Apps Script API and Google Sheets API:
# - https://console.cloud.google.com/marketplace/product/google/script.googleapis.com?authuser=6&project=summer-gadget-425314-e8
# - https://console.cloud.google.com/marketplace/product/google/sheets.googleapis.com?q=search&referrer=search&project=summer-gadget-425314-e8
# Set up this project in Apps Script project: https://console.developers.google.com/apis/credentials/consent?project=[PROJECT_ID]
# Download creds from here: clasp open --creds
#clasp setting projectId summer-gadget-425314-e8
#clasp login --creds creds.json
#clasp run getCurrentTimeUTCPlus8