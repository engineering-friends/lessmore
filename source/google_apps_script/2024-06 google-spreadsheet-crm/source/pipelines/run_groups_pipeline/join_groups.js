function join_groups({ started_at, sheet_name = "Groups" } = {}) {
  // - Get sheet

  const sheet =
    SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheet_name);

  // - Read existing data to avoid duplicates

  let indices = get_column_indices(sheet);
  let rows = sheet.getDataRange().getDisplayValues();

  for (let i = 1; i < rows.length; i++) {
    // - Get row

    let row = rows[i];
    // - Stop script if needed

    if (get_current_timestamp() - started_at > MAX_SCRIPT_RUNTIME_SECONDES) {
      SpreadsheetApp.flush();
      ScriptApp.stop();
    }

    // - Get code

    let code = row[indices["Code"]];
    if (code !== "" && code != "Error") {
      let status = row[indices["Status"]];
      // - Check if the group is already added

      if (status != "") {
        continue;
      }
      // - Add group

      let cellStatus = sheet.getRange(i + 1, indices["Status"] + 1);

      try {
        addInGroup({ invite_code: code });
        cellStatus.setValue("Success");
      } catch (e) {
        let statusCell = sheet.getRange(i + 1, indices["Status"] + 1);
        statusCell.setValue(e.message);
        post_event({
          text: `addGROUP____row=${i}_________${e.message}`,
          imageUrl: "",
          channel_id: DebugGroup,
        });
      }

      // - Flush

      SpreadsheetApp.flush();

      // - Random delay

      random_wait({ min: 10, max: 15 });
    }
  }
}
