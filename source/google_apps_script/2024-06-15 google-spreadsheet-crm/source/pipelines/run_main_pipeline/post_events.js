function send_messages_to_groups({ started_at, posts_sheet_name = "Posts" }) {
  console.log("Sending message to groups...");

  // - CLear the sheet if it's a new day

  console.log("Cleaning counter sheet...");

  clear_sheet_on_a_new_day();

  // - Get the sheet

  let sheet =
    SpreadsheetApp.getActiveSpreadsheet().getSheetByName(posts_sheet_name);
  if (!sheet) {
    Logger.log('No "Posts" sheet found.');
    return;
  }

  // - Get the column indices

  let indices = get_column_indices(sheet);

  // - Get the rows

  let rows = sheet.getDataRange().getDisplayValues();

  // - Get current date

  let now = getNewDate();

  // - Get group data

  let groupData = getGroupData(); // {group_id: {count: 0, groupName: "", indexRow: 0}}
  var sheetCountSend =
    SpreadsheetApp.getActiveSpreadsheet().getSheetByName("countSends");

  // - Process each row

  console.log("Starting to process rows");

  for (let i = 1; i < rows.length; i++) {
    // - Check if the script has been running for too long

    if (get_current_timestamp() - started_at > MAX_SCRIPT_RUNTIME_SECONDES) {
      SpreadsheetApp.flush();
      ScriptApp.stop();
    }

    // - Log

    if (i % 100 === 0) {
      console.log("Processed", i, "rows");
    }

    // - Get the row

    let row = rows[i];

    // - Unpack row

    let groupName = row[indices["GroupName"]];
    let chatId = row[indices["ChatID"]];
    let teacher = row[indices["Teacher"]];
    let messages = row[indices["Message"]].replace("@", teacher);
    let imageUrl = row[indices["ImageUrl"]];
    let currentStatus = row[indices["Status"]];
    let sendAfter = new Date(row[indices["SendAt"]]);

    // - Check status

    if (
      currentStatus === "Success" ||
      currentStatus === "Error" ||
      currentStatus === "Too Late"
    ) {
      console.log("Skip", groupName);
      continue; // Skip already successfully processed messages
    }

    // - Get the send before date

    let sendBefore = new Date(sendAfter.getTime() + 1 * 60 * 60 * 1000); // Adding 1 hour in milliseconds

    // - Update the group count

    if (now < sendAfter) {
      if (currentStatus !== "Too Early") {
        let statusCell = sheet.getRange(i + 1, indices["Status"] + 1);
        statusCell.setValue("Too Early");
      }
    } else if (now > sendBefore) {
      let statusCell = sheet.getRange(i + 1, indices["Status"] + 1);
      statusCell.setValue("Too Late");
    } else {
      try {
        // - Random sleep to avoid rate limiting

        random_wait({ min: 3, max: 5 });

        // - Get cells

        let statusCell = sheet.getRange(i + 1, indices["Status"] + 1);
        let processedAtCell = sheet.getRange(i + 1, indices["ProcessedAt"] + 1);
        let responseTextCell = sheet.getRange(i + 1, indices["Response"] + 1);

        // - Update the group count

        groupData = updateGroupCount(groupData, chatId, groupName);

        // - Check if the group has reached the limit

        if (groupData[chatId].count > MaxSendsInDay) {
          Logger.log(`alredy sent ${MaxSendsInDay} for ${groupName}`);
          statusCell.setValue("Error");
          responseTextCell.setValue(
            `alredy send ${MaxSendsInDay} message for ${groupName}`,
          );
          post_event({
            text: `alredy sent ${MaxSendsInDay} message for ${groupName}`,
            image_url: "",
            channel_id: DebugGroup,
          });
          continue;
        }

        // - Update the countSends sheet

        var indexRowSend = groupData[chatId].indexRow;
        sheetCountSend
          .getRange("A" + indexRowSend)
          .setValue(groupData[chatId].groupName);
        sheetCountSend.getRange("B" + indexRowSend).setValue(chatId);
        sheetCountSend
          .getRange("C" + indexRowSend)
          .setValue(groupData[chatId].count);

        // - Send the message

        let response = post_event({
          text: messages,
          image_url: imageUrl,
          channel_id: chatId,
        });

        // - Update the cells

        let responseCode = Number(response.getResponseCode());
        let responseText = response.getContentText();
        let processedAt = getNewDate();
        let lag = (processedAt - sendAfter) / 1000;

        processedAtCell.setValue(dateTimeToString(processedAt));

        if (responseCode >= 200 && responseCode < 300) {
          statusCell.setValue("Success");
          responseTextCell.setValue(responseText);

          let lagCell = sheet.getRange(i + 1, indices["Lag"] + 1);
          lagCell.setValue(lag);
        } else {
          statusCell.setValue("Error");
          responseTextCell.setValue(responseText);
        }
      } catch (error) {
        statusCell.setValue("Error");
        let e = error.toString();
        responseTextCell.setValue(e);
        post_event({
          text: `POST____row=${i}_________${e}`,
          image_url: "",
          channel_id: DebugGroup,
        });
      }
      // - Flush sheet

      SpreadsheetApp.flush();
    }
  }
  // - Flush sheet

  SpreadsheetApp.flush();
}

// Teacher's name
