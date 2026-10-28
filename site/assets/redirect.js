/* Keep existing bookmarks on the same project-site prefix and chapter. */
const target = new URL(document.getElementById('redirect-target').href);
target.search = window.location.search;
target.hash = window.location.hash;
window.location.replace(target.href);
