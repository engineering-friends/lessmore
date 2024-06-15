function get_column_indices(sheet, row = 1) {
  let headers = sheet
    .getRange(row, 1, 1, sheet.getLastColumn())
    .getDisplayValues()[0];
  let indexMap = {};
  headers.forEach((header, index) => {
    indexMap[header] = index;
  });
  return indexMap;
}

function getNewDate() {
  let originalDate = new Date();
  return new Date(
    originalDate.getTime() + originalDate.getTimezoneOffset() * 60 * 1000, // originalDate.getTimezoneOffset()  - returns the time zone difference, in minutes, from current locale (host system settings) to UTC (negative)
  );
}

function dateTimeToString(date) {
  let year = date.getFullYear();
  let month = (date.getMonth() + 1).toString().padStart(2, "0");
  let day = date.getDate().toString().padStart(2, "0");
  let hours = date.getHours().toString().padStart(2, "0");
  let minutes = date.getMinutes().toString().padStart(2, "0");
  let seconds = date.getSeconds().toString().padStart(2, "0");

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

function updateRowInPost(post_blueprint, index, sheet, indices) {
  Object.keys(post_blueprint).forEach((key) => {
    let _value = post_blueprint[key];

    let cell = sheet.getRange(index, indices[key] + 1);
    cell.setValue(_value);
  });
  let cell = sheet.getRange(index, indices["RowCreatedAt"] + 1);
  cell.setValue(dateTimeToString(getNewDate()));
}
