chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete") {
    chrome.scripting.executeScript({
      target: {tabId: tabId},
      function: reloadPage
    });
  }
});

function reloadPage() {
  setInterval(() => {
    location.reload();
  }, 60000);  // Reload every 60 seconds
}
