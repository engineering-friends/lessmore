// Existing message handling code
browser.runtime.sendMessage({ greeting: "hello" }).then((response) => {
    console.log("Received response: ", response);
});

browser.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log("Received request: ", request);
});

// New code to highlight elements
function highlightElements() {
    const elements = document.querySelectorAll('a[href="https://www.iana.org/domains/example"]');
    elements.forEach(element => {
        element.style.backgroundColor = 'yellow';
        element.style.border = '2px solid red';
    });
}

// Run the highlight function when the page is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', highlightElements);
} else {
    highlightElements();
}
