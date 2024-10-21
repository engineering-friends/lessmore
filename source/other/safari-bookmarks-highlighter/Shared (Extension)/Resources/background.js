browser.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log("Received request: ", request);

    if (request.greeting === "hello") {
        sendResponse({ farewell: "goodbye" });
        return true;
    }

    if (request.action === "getBookmarks") {
        browser.bookmarks.getTree().then((bookmarkTreeNodes) => {
            const bookmarks = flattenBookmarks(bookmarkTreeNodes);
            const response = { bookmarks: bookmarks.slice(0, 5) };
            console.log("Sending bookmarks:", response);
            sendResponse(response);
        }).catch((error) => {
            console.error("Error fetching bookmarks:", error);
            sendResponse({ error: error.toString() });
        });
        return true; // Indicates that we will send a response asynchronously
    }
});

function flattenBookmarks(bookmarkTreeNodes) {
    let bookmarks = [];
    for (const node of bookmarkTreeNodes) {
        if (node.url) {
            bookmarks.push({ title: node.title, url: node.url });
        }
        if (node.children) {
            bookmarks = bookmarks.concat(flattenBookmarks(node.children));
        }
    }
    console.log("Flattened bookmarks:", bookmarks);
    return bookmarks;
}
