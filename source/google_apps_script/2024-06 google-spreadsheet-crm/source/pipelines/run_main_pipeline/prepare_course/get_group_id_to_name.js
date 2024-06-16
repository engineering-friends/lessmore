function get_group_id_to_name() {
  let sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Groups");
  let indices = get_column_indices(sheet);
  let rows = sheet.getDataRange().getDisplayValues().slice(1);

  let results = {};

  rows.forEach((_row) => {
    results[_row[indices["GroupName"]]] = _row[indices["ChatID"]];
  });

  return results;
}
