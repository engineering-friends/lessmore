chrome.runtime.sendMessage({ action: "fetchBookmarks" }, (bookmarkLinks) => {
function highlightLinks() {
  const styleElement = document.createElement("style");
  document.head.appendChild(styleElement);
  const styleSheet = styleElement.sheet;

  const pageLinks = document.querySelectorAll("a");

  pageLinks.forEach((linkElement, index) => {
    const fullURL = new URL(linkElement.getAttribute('href'), window.location).toString();
    const matchedBookmark = bookmarkLinks.find(bookmark => fullURL.startsWith(bookmark));
    if (matchedBookmark) {
      // Apply the styles to gray-out the link
      linkElement.classList.add(`highlighted-link-${index}`);
      linkElement.style.setProperty("background-color", "rgba(24, 111, 101, 0.5)", "important");
      linkElement.style.setProperty("filter", "grayscale(100%)", "important");
      linkElement.style.setProperty("opacity", "0.75", "important");
    }
  });
}


  highlightLinks();

  // Re-apply every 5 seconds
  setInterval(highlightLinks, 500);
});
