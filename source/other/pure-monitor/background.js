chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === "complete") {
        chrome.scripting.executeScript({
            target: {tabId: tabId},
            function: reloadPage
        });
    }
});

function reloadPage() {
    chrome.storage.local.get(['hasFired'], function (result) {
        hasFired = result.hasFired || false; // Default to false if no value is stored

        if (!hasFired) {
            setInterval(() => {
                location.reload();
            }, (Math.floor(Math.random() * (75 - 45)) + 45) * 1000);  // Reload every 60 seconds on average
        }
    });
}
