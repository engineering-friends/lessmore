chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    console.log('Tab updated:', tabId, changeInfo, tab, tab.url);
    if (changeInfo.status === "complete" && tab.url && tab.url.includes('pure.app')) {

        chrome.storage.local.get(['hasFired', 'intervalId'], function (result) {
            hasFired = result.hasFired || false; // Default to false if no value is stored

            if (result.intervalId) {
                clearInterval(result.intervalId);
            }

            if (!hasFired) {
                intervalId = setInterval(() => {
                    chrome.tabs.query({}, function(tabs) {
                        for (let tab of tabs) {
                            console.log('Reloading tab:', tab.id, tab.url);
                            chrome.tabs.reload(tab.id); // Reload each relevant tab
                        }
                    });
                }, (Math.floor(Math.random() * 30) + 45) * 1000);  // Reload every 60 seconds on average

                // Store that the interval is set to avoid setting it again on reload
                chrome.storage.local.set({ intervalId: intervalId }, function () {
                    console.log('Interval has been set.');
                });
            }
        });
    }
});

