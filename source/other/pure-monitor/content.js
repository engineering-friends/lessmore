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
      linkElement.classList.add(`highlighted-link-${index}`);
      // linkElement.style.setProperty("border", "2px solid #186F65", "important");
      // linkElement.style.setProperty("border-radius", "8px", "important");
      // linkElement.style.setProperty("padding", "4px", "important");
      // linkElement.style.setProperty("color", "#186F65", "important");
      // linkElement.style.setProperty("background-color", "rgba(24, 111, 101, 0.5)", "important");
      styleSheet.insertRule(`.highlighted-link-${index}::after { content: " ✅"; }`, 0);
    }
  });
}




  highlightLinks();

  // Re-apply every 5 seconds
  setInterval(highlightLinks, 500);
});
