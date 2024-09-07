// Function to check the elements based on your conditions
function checkElements() {
  const elements = document.querySelectorAll('div.sc-jzNkva');

  elements.forEach(element => {
    // Condition 1: Check for "km" < 40 and "online"
    const distanceElement = element.querySelector('.sc-imwsjW span');
    const statusElement = element.querySelector('.sc-imwsjW span:last-child');

    if (distanceElement && statusElement) {
      const distanceText = distanceElement.textContent;
      const statusText = statusElement.textContent;

      // Extract km value
      const kmValue = parseInt(distanceText.replace(' km', ''));

      // Check if km is less than 40 and the status is 'online'
      if (kmValue < 40 && statusText.includes('online')) {

        // Condition 2: Make sure it doesn't contain "Gift sent"
        if (!element.innerHTML.includes('Gift sent')) {
          notifyUser("Condition Met: Online user within 40km");
        }
      }
    }
  });
}

// Function to send a browser notification
function notifyUser(message) {
  chrome.runtime.sendMessage({
    type: 'notification',
    message: message
  });
}

// Run the check function when the page loads
window.onload = () => {
  checkElements();
};

// Set up an interval to check every 30 seconds
setInterval(checkElements, 30000);
