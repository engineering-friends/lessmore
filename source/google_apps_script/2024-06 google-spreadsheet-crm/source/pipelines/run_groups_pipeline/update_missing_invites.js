function update_missing_invites({ started_at, sheet_name = "Groups" } = {}) {
  // - Get sheet

  const sheet =
    SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheet_name);

  // - Read existing data to avoid duplicates

  let rows = sheet.getDataRange().getDisplayValues();

  // - Get indices

  let indices = get_column_indices(sheet);

  for (let i = 1; i < rows.length; i++) {
    let row = rows[i];
    if (row[indices["Code"]] == "") {
      // - Stop script if needed

      if (get_current_timestamp() - started_at > MAX_SCRIPT_RUNTIME_SECONDES) {
        SpreadsheetApp.flush();
        ScriptApp.stop();
      }

      // - Update invite code

      console.log("Updating invite", row[indices["ChatID"]]);

      let invite_code_cell = sheet.getRange(i + 1, indices["Code"] + 1);
      try {
        let invite = getInviteAPI({
          groupID: row[indices["ChatID"]].replace("@", "%40"),
        }).invite_code;
        invite_code_cell.setValue(invite);
      } catch (e) {
        let statusCell = sheet.getRange(i + 1, indices["Status"] + 1);
        statusCell.setValue(e.message);

        invite_code_cell.setValue("Error");
        post_event({
          text: `GET_INVITE____row=${i}_________${e.message}`,
          image_url: "",
          channel_id: DebugGroup,
        });
      }

      // - Flush spreadshseet

      SpreadsheetApp.flush();

      // - Wait random time to avoid rate limits

      random_wait({ min: 10, max: 15 });
    }
  }
}
