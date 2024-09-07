

// Function to check if conditions are met and notify
function checkConditionsAndNotify() {

  const elements = document.querySelectorAll('div.sc-jzNkva');
  console.log('Elements:', elements);

  elements.forEach((element) => {
    const lastSeenSpans = element.querySelectorAll('span.sc-imwsjW span');

    if (!element.textContent.includes('Gift sent')) {
      let distance = 0;
      let lastSeenStatus = '';

      // Get the distance and last seen status
      if (lastSeenSpans.length >= 2) {
        distance = parseFloat(lastSeenSpans[0].textContent);
        lastSeenStatus = lastSeenSpans[1].textContent.trim();
      }

      console.log('Distance:', distance);
      console.log('Last seen status:', lastSeenStatus);
      console.log('Element text:', element.textContent);
      console.log('Spans:', lastSeenSpans);
      console.log('---');

      // Check if distance is less than 40 and last seen status is "online"
      if (distance < 40 && lastSeenStatus.toLowerCase() === 'online') {
        // Create notification
        alert('Notification: Found a match with distance less than 40 km and online status!');
      }
    }
  });
}

// Call the function when the page loads
window.addEventListener('load', () => {
  // Play sound notification
  const audio = new Audio(chrome.runtime.getURL('notification.mp3'));
  audio.play();

  // sleep for 10 seconds
  setTimeout(() => {
    checkConditionsAndNotify();
  }, 5000);

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
