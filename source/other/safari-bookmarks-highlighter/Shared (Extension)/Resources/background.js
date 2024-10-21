browser.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log("Received request: ", request);

    if (request.greeting === "hello")
        return Promise.resolve({ farewell: "goodbye" });

    if (request.action === "getBookmarks") {
        return browser.bookmarks.getTree().then((bookmarkTreeNodes) => {
            const bookmarks = flattenBookmarks(bookmarkTreeNodes);
            return { bookmarks: bookmarks.slice(0, 5) };
        });
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
    return bookmarks;
}
