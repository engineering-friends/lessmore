chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'fetchBookmarks') {
    chrome.bookmarks.getTree((bookmarkTreeNodes) => {
      const bookmarkLinks = [];
      function extractBookmarks(bookmarkNode) {
        if (bookmarkNode.url) {
          bookmarkLinks.push(bookmarkNode.url);
        }
        if (bookmarkNode.children) {
          bookmarkNode.children.forEach(extractBookmarks);
        }
      }
      bookmarkTreeNodes.forEach(extractBookmarks);
      sendResponse(bookmarkLinks);
    });
    return true;
  }
});
