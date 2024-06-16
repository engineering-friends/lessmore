function inflate_groups({ sheet_name = "Groups" } = {}) {
  try {
    // - Get sheet and create if not exists

    const sheet =
      SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheet_name);
    if (!sheet) {
      // Create a new sheet named 'Groups' if it doesn't exist
      SpreadsheetApp.getActiveSpreadsheet().insertSheet(sheet_name);
    }

    // - Read existing data to avoid duplicates

    const range = sheet.getDataRange();
    const values = range.getDisplayValues();
    let existingGroups = new Map();
    values.forEach((row) => {
      existingGroups.set(row[1], true); // Assuming Chat ID is in column 2 (B)
    });

    // - Fetch groups from WhatsApp API

    let offset = 0;
    const limit = 500; // 500 is max limit in whapi.cloud
    while (true) {
      // - Get groups

      let fetchedGroups = getGroups(offset, limit);
      let groups = fetchedGroups.groups;

      console.log("Got groups:", groups.length);

      // - Append only new groups with a timestamp in batch

      let newRows = [];
      groups.forEach(function (group) {
        if (!existingGroups.has(group.id)) {
          const timestamp = Utilities.formatDate(
            new Date(),
            Session.getScriptTimeZone(),
            "yyyy-MM-dd HH:mm:ss",
          );
          newRows.push([group.name, group.id, timestamp]);

          Logger.log("Added new group: " + group.name + ", " + group.id);
        } else {
          Logger.log(
            "Group already exists, skipping: " + group.name + ", " + group.id,
          );
        }
      });

      if (newRows.length > 0) {
        sheet
          .getRange(
            sheet.getLastRow() + 1,
            1,
            newRows.length,
            newRows[0].length,
          )
          .setValues(newRows);
      }

      offset += limit;
      if (groups.length != limit) {
        return;
      }
    }
  } catch (error) {
    Logger.log("Error:", error.toString()); // Log any errors that occur during execution
  }
}
