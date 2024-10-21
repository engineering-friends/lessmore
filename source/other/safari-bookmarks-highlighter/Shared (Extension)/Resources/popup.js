document.addEventListener('DOMContentLoaded', function () {
    const bookmarkList = document.getElementById('bookmarkList');

    browser.runtime.sendMessage({ action: "getBookmarks" })
        .then((response) => {
            console.log("Received response:", response);
            if (response.error) {
                throw new Error(response.error);
            }
            if (!response.bookmarks || !Array.isArray(response.bookmarks)) {
                throw new Error("Invalid bookmarks data received");
            }
            console.log("Received bookmarks:", response.bookmarks);
            if (response.bookmarks.length === 0) {
                bookmarkList.innerHTML = "<li>No bookmarks found</li>";
            } else {
                response.bookmarks.forEach((bookmark) => {
                    console.log("Processing bookmark:", bookmark);
                    const li = document.createElement('li');
                    const a = document.createElement('a');
                    a.href = bookmark.url;
                    a.textContent = bookmark.title || "Untitled";
                    a.target = '_blank';
                    li.appendChild(a);
                    bookmarkList.appendChild(li);
                });
            }
        })
        .catch((error) => {
            console.error('Error fetching bookmarks:', error);
            bookmarkList.innerHTML = `<li>Error: ${error.message}</li>`;
        });
});
