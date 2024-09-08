document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('resetBtn').addEventListener('click', function () {
        // Send a message to the content script to reset the flag
        chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
            chrome.tabs.sendMessage(tabs[0].id, {action: "resetHasFired"});
        });
    });
});
