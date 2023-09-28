chrome.runtime.sendMessage({action: 'fetchBookmarks'}, (bookmarkLinks) => {
  const pageLinks = document.querySelectorAll("a");
  pageLinks.forEach((linkElement) => {
    if (bookmarkLinks.includes(linkElement.href)) {
      linkElement.style.backgroundColor = "yellow";
    }
  });
});
