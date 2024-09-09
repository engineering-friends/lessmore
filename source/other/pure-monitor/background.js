// global service worker

import { sendNotification } from './utils/send_notification.js';

sendNotification('Service worker started');

console.log('Service worker started'); // see the logs at extensions page -> Inspect views service worker

// - Add listener to reload the page every 60 seconds

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === "loading" && tab.url && (tab.url.includes('pure.app') || tab.url.includes('bumble.com'))) {

        chrome.storage.local.get(['hasFired'], function (result) {
            // - Get hasFired

            hasFired = result.hasFired || false; // Default to false if no value is stored

            // - Return if already fired

            if (hasFired) {
                console.log('Already fired, skipping');
                return;
            }

            // - Reload current tab in 60 seconds

            setInterval(() => {
                chrome.tabs.reload(tabId); // Reload current tab
            }, (Math.floor(Math.random() * 30) + 45) * 1000);  // Reload every 60 seconds on average
        });
    }
});

