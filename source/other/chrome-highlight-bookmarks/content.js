chrome.runtime.sendMessage({ action: "fetchBookmarks" }, (bookmarkLinks) => {
  const observer = new MutationObserver(() => {
    const pageLinks = document.querySelectorAll("a");
    pageLinks.forEach((linkElement) => {
      const matchedBookmark = bookmarkLinks.find(bookmark => linkElement.href.startsWith(bookmark));
      if (matchedBookmark) {
        linkElement.style.color = "#186F65";
      }
    });
  });

  observer.observe(document.body, { childList: true, subtree: true });
});
