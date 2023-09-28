chrome.runtime.sendMessage({ action: "fetchBookmarks" }, (bookmarkLinks) => {
  function highlightLinks() {
    const pageLinks = document.querySelectorAll("a");

    pageLinks.forEach((linkElement) => {
      const fullURL = new URL(linkElement.getAttribute('href'), window.location).toString();
      const matchedBookmark = bookmarkLinks.find(bookmark => fullURL.startsWith(bookmark));
      if (matchedBookmark) {
       linkElement.style.color = "#186F65";
      }
    });
  }

  highlightLinks();

  // Re-apply every 5 seconds
  setInterval(highlightLinks, 500);
});
