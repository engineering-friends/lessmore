// Flag to check if alert has already fired
let hasFired = false;

// Function to check if conditions are met and notify
function checkConditionsAndNotify() {
  // If alert has already fired, do nothing
  if (hasFired) return;

  // check for a new message
  if (document.querySelector('div.sc-cepbVR')) { // black dot of unread message
    hasFired = true;
    sendNotification();
  }

  const elements = document.querySelectorAll('div.sc-jzNkva'); // posts

  elements.forEach((element) => {
    const giftSentText = element.querySelector('span')?.textContent || '';
    const lastSeenSpans = element.querySelectorAll('span.sc-imwsjW span'); // 6km, online

    // Condition 1: Does not contain "Gift sent"
    if (!giftSentText.includes('Gift sent')) {
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
        sendNotification();
      }
    }
  });
}

// Function to send the POST request
function sendNotification() {
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
      "body": "Ping"
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
  // Check the conditions after page load
  checkConditionsAndNotify();

  // Create "Hello World" notification (for debugging purposes)
  const helloWorldDiv = document.createElement('div');
  helloWorldDiv.textContent = 'Hello world';
  helloWorldDiv.style.position = 'fixed';
  helloWorldDiv.style.top = '10px';
  helloWorldDiv.style.right = '10px';
  helloWorldDiv.style.backgroundColor = 'white';
  helloWorldDiv.style.padding = '10px';
  helloWorldDiv.style.border = '1px solid black';
  helloWorldDiv.style.zIndex = '10000';
  document.body.appendChild(helloWorldDiv);
});
