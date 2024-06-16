function clear_sheet_on_a_new_day() {
  var sheet =
    SpreadsheetApp.getActiveSpreadsheet().getSheetByName("countSends");

  if (sheet) {
    var firstCell = sheet.getRange("A1").getValue();

    if (firstCell instanceof Date) {
      var today = new Date();
      today.setHours(0, 0, 0, 0); // Устанавливаем время в 0, чтобы сравнивать только дату

      // Получаем дату из ячейки A1 и приводим её к формату даты без времени
      var firstDate = new Date(firstCell);
      firstDate.setHours(0, 0, 0, 0); // Устанавливаем время в 0, чтобы сравнивать только дату

      // Сравниваем текущую дату с датой в ячейке A1
      if (today.getTime() !== firstDate.getTime()) {
        sheet.clear(); // Очищаем лист, если даты не совпадают
        // Записываем текущую дату в ячейку A1
        sheet.getRange("A1").setValue(today);
        // Добавляем заголовки
        sheet
          .getRange("A2:C2")
          .setValues([["groupName", "groupID", "countSends"]]);
      }
    } else {
      Logger.log("Ячейка A1 не содержит дату.");
      // Если ячейка A1 не содержит дату, очищаем лист и записываем текущую дату и заголовки
      sheet.clear();
      var today = new Date();
      sheet.getRange("A1").setValue(today);
      sheet
        .getRange("A2:C2")
        .setValues([["groupName", "groupID", "countSends"]]);
    }
  } else {
    Logger.log("Лист с именем " + SheetNameForCountPost + " не найден.");
  }
}

function getGroupData() {
  var sheet =
    SpreadsheetApp.getActiveSpreadsheet().getSheetByName("countSends");

  if (!sheet) {
    Logger.log("Лист с именем " + SheetNameForCountPost + " не найден.");
    return;
  }

  var data = sheet.getDataRange().getValues();
  var groupData = {};

  // Проверяем, что есть хотя бы две строки данных (заголовки и одна строка данных)
  if (data.length > 2) {
    for (var i = 2; i < data.length; i++) {
      var groupID = data[i][1];
      var groupName = data[i][0];
      var sendCount = data[i][2];
      groupData[groupID] = {
        groupName: groupName,
        count: sendCount,
        indexRow: i + 1,
      };
    }
  }

  return groupData;
}

function updateGroupCount(groupData, groupID, groupName) {
  if (groupID in groupData) {
    groupData[groupID].count += 1;
  } else {
    groupData[groupID] = {
      groupName: groupName,
      count: 1,
      indexRow: Object.keys(groupData).length + 3,
    };
  }
  return groupData;
}
