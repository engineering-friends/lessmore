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
      // - Make element disappear
      linkElement.classList.add(`highlighted-link-${index}`);
      linkElement.style.setProperty("opacity", "0", "important");

      // - Make parent element with thumbnail disappear

    // Assuming linkElement is the current <a> element
      let parentElement = linkElement.parentElement;

      while (parentElement) {
        let hasThumbnailInAttribute = false;

        // Loop through all attributes of the current element
        for (let attr of parentElement.attributes) {
          if ((attr.name.toLowerCase().includes('thumbnail'))  || (attr.value.toLowerCase().includes('thumbnail'))) {
            hasThumbnailInAttribute = true;
            break;
          }
        }

        if (hasThumbnailInAttribute) {
          break; // Found the element with "thumbnail" in the attribute name
        }

        parentElement = parentElement.parentElement; // Move to the next parent
      }

      if (parentElement) {
        parentElement.style.setProperty("opacity", "0", "important");
      }

    }
  });
}


  highlightLinks();

  // Re-apply every 5 seconds
  setInterval(highlightLinks, 500);
});
