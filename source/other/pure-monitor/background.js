chrome.runtime.onInstalled.addListener(() => {
  chrome.alarms.create('refreshAlarm', { periodInMinutes: 0.5 }); // 30 seconds
});

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'refreshAlarm') {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      chrome.scripting.executeScript({
        target: { tabId: tabs[0].id },
        function: refreshPage
      });
    });
  }
});

function refreshPage() {
  window.location.reload();
}
