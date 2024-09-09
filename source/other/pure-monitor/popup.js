document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('resetBtn').addEventListener('click', function () {
        // - Log
        console.log('Reset button clicked.');
        // - Reset hasFired flag
        chrome.storage.local.set({hasFired: false}, function () {
            console.log('hasFired has been reset to false.');
        });
        // - Reload all tabs
        chrome.tabs.query({}, function(tabs) {
            for (let tab of tabs) {
                console.log('Reloading tab:', tab.id, tab.url);
                chrome.tabs.reload(tab.id); // Reload each relevant tab
            }
        });
    });
});
