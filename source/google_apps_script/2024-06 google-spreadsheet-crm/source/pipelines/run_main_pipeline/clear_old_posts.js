function clear_old_posts({
  sheet_name = "Posts",
  ttl_seconds = 10 * 24 * 60 * 60, // 10 days
} = {}) {
  console.log("Clearing old posts...");
  // - Get sheet

  let sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheet_name);

  // - Get indices

  let indices = get_column_indices(sheet);

  // - Get rows

  let rows = sheet.getDataRange().getValues().slice(1);

  let deleted_counter = 0;

  rows.forEach((_row, index) => {
    // - Get date difference

    let diff =
      get_current_timestamp() -
      new Date(_row[indices["SendAt"]]).getTime() / 1000;

    // - Delete if older than 30 days

    if (diff > ttl_seconds || isNaN(diff)) {
      sheet.deleteRow(index + 2 - deleted_counter);
      deleted_counter += 1;
      console.log("Deleting row", _row[indices["SendAt"]]);
    }
  });

  // - Flush

  SpreadsheetApp.flush();
}
