document.addEventListener('DOMContentLoaded', function () {
    browser.runtime.sendMessage({ action: "getBookmarks" })
        .then((response) => {
            const bookmarkList = document.getElementById('bookmarkList');
            response.bookmarks.forEach((bookmark) => {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = bookmark.url;
                a.textContent = bookmark.title;
                a.target = '_blank';
                li.appendChild(a);
                bookmarkList.appendChild(li);
            });
        })
        .catch((error) => {
            console.error('Error fetching bookmarks:', error);
        });
});
