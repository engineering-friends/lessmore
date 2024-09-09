// // content.js runs for every tab that matches the URL patterns in manifest.json
//
// // - Get hasFired from storage or set it to false by default
//
// let hasFired = false;
//
// chrome.storage.local.get(['hasFired'], function (result) {
//     hasFired = result.hasFired || false; // Default to false if no value is stored
//     console.log('Initial hasFired value:', hasFired);
// });
//
// // - Add listener to check 5 seconds after page load
//
// window.addEventListener('load', () => {
//     // wait for 5 seconds for page to load and then check the conditions
//     setTimeout(checkConditionsAndNotify, 5000);
// });
//
//
// // Function to check if conditions are met and notify
// function checkConditionsAndNotify() {
//     // - Return if already fired
//
//     if (hasFired) return;
//
//     // - Get url
//
//     const url = window.location.href;
//
//     // - Pure
//
//     if (url.includes('pure.app')) {
//
//         // check for a new message (disabled for now)
//         if (document.querySelector('div.sc-cepbVR')) { // black dot of unread message
//             fireEventAndNotify("New message");
//             return;
//         }
//
//         const elements = document.querySelectorAll('div.sc-jzNkva'); // posts
//
//         for (let element of elements) {
//             const lastSeenSpans = element.querySelectorAll('span.sc-imwsjW span'); // 6km, online
//
//             if (!element.textContent.includes('Gift sent')) {
//                 let distance = 0;
//                 let lastSeenStatus = '';
//
//                 // Get the distance and last seen status
//                 if (lastSeenSpans.length >= 2) {
//                     distance = parseFloat(lastSeenSpans[0].textContent);
//                     lastSeenStatus = lastSeenSpans[1].textContent.trim();
//                 }
//
//                 // Check if distance is less than 40 and last seen status is "online"
//                 if (distance < 40 && lastSeenStatus.toLowerCase() === 'online') {
//                     fireEventAndNotify("New user");
//
//                     break;
//                 }
//             }
//         }
//     }
//
//     // - Bumble
//
//     // check if 'body' has text "Want to keep matching?"
//     if (url.includes('bumble.com')) {
//         if (!document.querySelector('body').textContent.includes('Want to keep matching?')) {
//             fireEventAndNotify("New animal");
//         }
//     }
// }
//
//
// // A helper function to set hasFired and send notification
// function fireEventAndNotify(message) {
//     hasFired = true;
//     chrome.storage.local.set({ hasFired: true }, function () {
//         console.log('hasFired value stored as true.');
//     });
//
//     fetch('https://gate.whapi.cloud/messages/text', {
//         method: 'POST',
//         headers: {
//             'accept': 'application/json',
//             'authorization': 'Bearer IOdPDCsh4ByBUdtGmogSUtNeacbusFv4',
//             'content-type': 'application/json'
//         },
//         body: JSON.stringify({
//             "typing_time": 0,
//             "to": "995551185124",
//             "body": message
//         })
//     })
//         .then(response => response.json())
//         .then(data => {
//             console.log('Notification sent successfully:', data);
//         })
//         .catch(error => {
//             console.error('Error sending notification:', error);
//         });
//
// }
//
