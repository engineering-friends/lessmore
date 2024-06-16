const TOKEN = "";

function checkFlightAndNotify() {
  var url = "https://ticket.vanillasky.ge/custom/check-flight/6/7";
  var expectedDates = [
    "2024-06-07",
    "2024-06-09",
    "2024-06-10",
    "2024-06-12",
    "2024-06-11",
    "2024-06-13",
    "2024-06-14",
    "2024-06-16",
  ];

  var response = UrlFetchApp.fetch(url);
  var json = JSON.parse(response.getContentText());

  var toDates = json.to;
  var fromDates = json.from;

  var allDates = toDates.concat(fromDates);

  var properties = PropertiesService.getScriptProperties();
  var sentNotification = properties.getProperty("sentNotification") === "true";

  // Check if there are new dates and if notification hasn't been sent yet
  if (newDatesPresent(allDates, expectedDates) && !sentNotification) {
    sendNotification();
    properties.setProperty("sentNotification", "true");
    console.log("New dates found, sent notification!");
  }

  if (sentNotification) {
    console.log("Already sent!");
  } else {
    console.log("No new dates found");
  }
}

function newDatesPresent(allDates, expectedDates) {
  var setExpected = new Set(expectedDates);
  for (let date of allDates) {
    if (!setExpected.has(date)) {
      return true;
    }
  }
  return false;
}

function sendNotification() {
  var url = "https://gate.whapi.cloud/messages/text";
  var payload = {
    typing_time: 0,
    to: "995551185124",
    body: "New tickets available from Mestia to Natakhtari!",
  };

  var options = {
    method: "post",
    contentType: "application/json",
    headers: {
      accept: "application/json",
      authorization: "Bearer " + TOKEN,
    },
    payload: JSON.stringify(payload),
  };

  var response = UrlFetchApp.fetch(url, options);
  Logger.log(response.getContentText());
}

function resetNotification() {
  // Function to manually reset the notification flag if needed
  PropertiesService.getScriptProperties().setProperty(
    "sentNotification",
    "false",
  );
}
