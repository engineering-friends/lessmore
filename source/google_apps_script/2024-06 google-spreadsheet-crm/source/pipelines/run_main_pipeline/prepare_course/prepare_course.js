function prepare_course({
  prefix = "Course",
  posts_sheet_name = "Posts",
} = {}) {
  console.log("Preparing courses...");
  updatePosts({
    activity_posts: get_activity_posts({ prefix: prefix }),
    posts_sheet_name: posts_sheet_name,
  });
}

function getAllListWithCource({ prefix }) {
  let spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  let sheets = spreadsheet.getSheets();

  return sheets
    .filter((sheet) => sheet.getName().startsWith(prefix))
    .map((sheet) => sheet.getName());
}

function get_activity_posts({ prefix = "Course" }) {
  // read all posts with future date
  /*
       {
       "6_120363044849163604@g.us_1986730790": {
      "GroupName": "Group test current account 2",
      "Message": "Hanya saja, jangan terpaku!\n\nHalo orang tua!\nAnak-anak menguasai algoritma jenis baru di mana beberapa langkah diulang beberapa kali atau tak terbatas. Saya ingin membagikan hasil siswa pada pelajaran dengan topik “Siklus”:",
      "SheetID": 1986730790,
      "Teacher": "Isar The Sky",
      "ImageUrl": "https://drive.google.com/file/d/1tTOMPCLBBJOhTtwuKFbU5L3lA82MO_PO/view?usp=drive_link",
      "ActivityUniqueKey": "6",
      "SendAt": "2024-06-04 07:10:00",
      "ChatID": "120363044849163604@g.us"
    },...
 }
  * */
  console.log("Getting activity posts...");
  let coursesList = getAllListWithCource({ prefix: prefix });
  let courseData = {};
  let group_id_to_name = get_group_id_to_name();

  coursesList.forEach((sheetName) => {
    getDataInList(
      (listName = sheetName),
      (results = courseData),
      (groupInfo = group_id_to_name),
    );
  });
  return courseData;
}

function getDataInList(listName, results, groupInfo) {
  console.log("Getting data in list", listName);

  let sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(listName);
  let sheet_id = sheet.getSheetId();
  let indices = get_column_indices(sheet, 3); // Adjusted row for indices

  if (!sheet) {
    console.log("Лист с именем", listName, "не найден.");
    return [];
  }

  let values = sheet.getDataRange().getDisplayValues();

  let allGroupName = values[NumberRowFromGroupName + 1].slice(
    NumberColumnFromGroupName,
  ); // Adjusted row for group names
  let valuesWithData = values.slice(NumberRowWithData + 1); // Adjusted row for data

  valuesWithData.forEach((_rowValues, index) => {
    let activity = _rowValues[indices["ActivityUniqueKey"]];
    let text = _rowValues[indices["Message"]];
    let imageUrl = _rowValues[indices["ImageUrl"]];

    let cellStatus = sheet.getRange(
      index + NumberRowWithData + 2, // Adjusted row for status cell
      indices["Status"] + 1,
    );

    allGroupName.forEach((groupName, i) => {
      let teacher = values[0][NumberColumnFromGroupName + i]; // Adjusted row for teacher
      let comment = values[1][NumberColumnFromGroupName + i]; // not used for now

      let sendAt = _rowValues[NumberColumnFromGroupName + i];
      if (sendAt === "") {
        return;
      }
      if (groupName === "") {
        return;
      }

      sendAt = new Date(sendAt);
      sendAt.setHours(sendAt.getHours() - DiffTimeZoneHours);

      let now = new Date();
      let now_utc = new Date(
        now.getTime() + now.getTimezoneOffset() * 60 * 1000,
      );

      if (now_utc > sendAt) {
        return;
      }

      let groupID = groupInfo[groupName];

      cellStatus.setValue(`Last prepare row ${dateTimeToString(now)}`);

      results[`${activity}_${groupID}_${sheet_id}`] = {
        ActivityUniqueKey: activity,
        Message: text,
        ImageUrl: imageUrl,
        SendAt: dateTimeToString(sendAt),
        GroupName: groupName,
        ChatID: groupID,
        SheetID: sheet_id,
        Teacher: teacher,
      };
    });
  });
}
function updatePosts({ activity_posts, posts_sheet_name }) {
  console.log("Updating posts...");

  // - Get sheet
  let sheet =
    SpreadsheetApp.getActiveSpreadsheet().getSheetByName(posts_sheet_name);

  // - Get indices
  let indices = get_column_indices(sheet);

  // - Get rows

  let rows = sheet.getDataRange().getValues().slice(1);

  // - Get group_id_to_name

  let group_id_to_name = get_group_id_to_name();

  // - Update old

  console.log("Updating activities...");

  rows.forEach((row, i) => {
    // - Return if status is Success, Errors, Too Late

    let status = row[indices["Status"]];

    if (["Success", "Errors", "Too Late"].includes(status)) {
      return;
    }

    // - Update row if it is in activity_posts

    let activity = row[indices["ActivityUniqueKey"]];
    let groupName = row[indices["GroupName"]];
    let sheetID = row[indices["SheetID"]];
    let groupID = group_id_to_name[groupName];

    let _key = `${activity}_${groupID}_${sheetID}`;
    let _index = Object.keys(activity_posts).indexOf(_key);

    if (_index !== -1) {
      let post_blueprint = activity_posts[_key];

      // Check if any values have changed
      let rowHasChanged = Object.keys(post_blueprint).some(
        (key) => post_blueprint[key] !== row[indices[key]],
      );

      if (rowHasChanged) {
        updateRowInPost(
          post_blueprint,
          (index = i + 2),
          (sheet = sheet),
          (indices = indices),
        );
      }

      delete activity_posts[_key];
    }
  });

  // - Add new

  console.log("Adding new activities...");

  let lengthOldData = rows.length;
  let dataToUpdate = [];

  Object.keys(activity_posts).forEach((key, index) => {
    let post_blueprint = activity_posts[key];
    let rowIndex = index + 2 + lengthOldData;

    Object.keys(post_blueprint).forEach((key) => {
      let _value = post_blueprint[key];
      let cellAddress = {
        row: rowIndex,
        column: indices[key] + 1,
        value: _value,
      };
      dataToUpdate.push(cellAddress);
    });

    // Add RowCreatedAt update
    let rowCreatedAtAddress = {
      row: rowIndex,
      column: indices["RowCreatedAt"] + 1,
      value: dateTimeToString(getNewDate()),
    };
    dataToUpdate.push(rowCreatedAtAddress);
  });

  console.log("Setting values for activities:", dataToUpdate.length);

  // Perform the batch update
  dataToUpdate.forEach((cellInfo) => {
    let cell = sheet.getRange(cellInfo.row, cellInfo.column);
    cell.setValue(cellInfo.value);
  });

  // - Flush

  console.log("Flushing...");

  SpreadsheetApp.flush();
}
