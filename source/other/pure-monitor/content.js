// Flag to check if alert has already fired
let hasFired = false;

// Function to check if conditions are met and notify
function checkConditionsAndNotify() {
  // If alert has already fired, do nothing
  if (hasFired) return;

  // check for a new message
  if (document.querySelector('div.sc-cepbVR')) { // black dot of unread message
    hasFired = true;
    sendNotification("New message");
    return;
  }

  const elements = document.querySelectorAll('div.sc-jzNkva'); // posts

  elements.forEach((element) => {
    const lastSeenSpans = element.querySelectorAll('span.sc-imwsjW span'); // 6km, online

    // Condition 1: Does not contain "Gift sent"
    if (!element.textContent.includes('Gift sent')) {
      let distance = 0;
      let lastSeenStatus = '';

      // Get the distance and last seen status
      if (lastSeenSpans.length >= 2) {
        distance = parseFloat(lastSeenSpans[0].textContent);
        lastSeenStatus = lastSeenSpans[1].textContent.trim();
      }

      // Check if distance is less than 40 and last seen status is "online"
      if (distance < 40 && lastSeenStatus.toLowerCase() === 'online') {
        // Set the hasFired flag to true to prevent further execution
        hasFired = true;

        // Send the POST request using fetch
        sendNotification("New user");
      }
    }
  });
}

// Function to send the POST request
function sendNotification(text) {
  fetch('https://gate.whapi.cloud/messages/text', {
    method: 'POST',
    headers: {
      'accept': 'application/json',
      'authorization': 'Bearer ...',
      'content-type': 'application/json'
    },
    body: JSON.stringify({
      "typing_time": 0,
      "to": "995551185124",
      "body": text
    })
  })
      .then(response => response.json())
      .then(data => {
        console.log('Notification sent successfully:', data);
      })
      .catch(error => {
        console.error('Error sending notification:', error);
      });
}

// Reset the hasFired flag when the page is manually reloaded
window.addEventListener('beforeunload', () => {
  hasFired = false;
});

// Call the function when the page loads
window.addEventListener('load', () => {
  // wait for 5 seconds for page to load and then check the conditions
  setTimeout(checkConditionsAndNotify, 5000);
});

// Listen for the reset message from the popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "resetHasFired") {
    hasFired = false;  // Reset the hasFired flag
    console.log('Extension has been reset. hasFired is now:', hasFired);
  }
});