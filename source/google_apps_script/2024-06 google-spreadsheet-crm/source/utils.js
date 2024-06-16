// - Infinite scripts

function cleanTriggers(functionName) {
  const existingTriggers = ScriptApp.getProjectTriggers();
  for (let trigger of existingTriggers) {
    if (trigger.getHandlerFunction() == functionName) {
      ScriptApp.deleteTrigger(trigger);
    }
  }
}

function scheduleNextExecution(functionName, period) {
  // - First, clear existing triggers to avoid duplicates

  const existingTriggers = ScriptApp.getProjectTriggers();
  for (let trigger of existingTriggers) {
    if (trigger.getHandlerFunction() == functionName) {
      ScriptApp.deleteTrigger(trigger);
    }
  }

  // - Create a new trigger to run 'performTask' in a few minutes

  ScriptApp.newTrigger(functionName)
    .timeBased()
    .after(period * 1000)
    .create();
}

// - Singleton execution

function lock(appName) {
  var scriptProperties = PropertiesService.getScriptProperties();
  scriptProperties.setProperty(appName + "IsLocked", "True");
}

function isLocked(appName) {
  var scriptProperties = PropertiesService.getScriptProperties();
  return scriptProperties.getProperty(appName + "IsLocked") == "True";
}

function unlock(appName) {
  var scriptProperties = PropertiesService.getScriptProperties();
  scriptProperties.setProperty(appName + "IsLocked", "");
}

// - Locks

function unlockSheet(lock) {
  lock.remove();
}

function lockSheet(sheet) {
  const protection = sheet.protect();
  protection.setDescription("MyApplication Lock");
  protection.setWarningOnly(true);
  return protection;
}
function lockAllSheets() {
  const sheets = SpreadsheetApp.getActiveSpreadsheet().getSheets();
  sheets.forEach((sheet) => {
    lockSheet(sheet);
  });
}

function unlockAllSheets() {
  const sheets = SpreadsheetApp.getActiveSpreadsheet().getSheets();
  sheets.forEach((sheet) => {
    unlockSheet(lockSheet(sheet));
  });
}

// - Get current timestamp

function get_current_timestamp() {
  let current_date = new Date();
  return current_date.getTime() / 1000 + current_date.getTimezoneOffset() * 60; // originalDate.getTimezoneOffset()  - returns the time zone difference, in minutes, from current locale (host system settings) to UTC (negative)
}

// - Random wait

function random_wait({ min, max }) {
  Utilities.sleep((Math.floor(Math.random() * (max - min + 1)) + min) * 1000);
}
