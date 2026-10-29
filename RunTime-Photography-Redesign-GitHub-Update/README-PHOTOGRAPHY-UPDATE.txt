RUNTIME DIVE SYSTEMS — PHOTOGRAPHY REDESIGN
=========================================

Contents
--------
assets/site.css     Updated responsive gallery, homepage preview, and full-screen photo viewer styling.
assets/site.js      Updated viewer navigation and mobile swipe support; existing software/design behavior retained.

Installation (GitHub website)
-----------------------------
1. Unzip this file on your Mac.
2. Open https://github.com/Jdd227/runtime-dive-systems
3. Choose Add file > Upload files.
4. Drag the "assets" folder from this package, or drag site.css and site.js into the assets folder in GitHub.
5. Commit the replacement files to the main branch.
6. In Actions, check the Publish RunTime workflow finishes successfully.
7. Refresh https://runtimedivesystems.com/photos/ (hard refresh if your browser cached the old CSS or JS).

What changes
------------
* Photography page: 3-column editorial masonry layout on wide screens, 2 columns on mobile.
* Photographs keep their natural proportions in the gallery instead of uniform crops.
* The home page Photography feature has one larger image plus two smaller images.
* Lightbox opens full images, with previous/next buttons, arrow keys, Escape key, and touch swipe.
* A small gallery count is added automatically; no manual changes needed when new photos are uploaded.
* Visible photo captions remain hidden; image alt text remains available for accessibility.
* Existing photos, gallery.json, design pages, blog, and downloadable STL files are unchanged.

Adding more photos
------------------
No change to your workflow: upload photos to assets/photos/, then add a matching entry to content/gallery.json. The new layout works with any gallery length.

Technical validation
--------------------
* Browser DOM tests passed for 40 photos, desktop/mobile columns, viewer arrows, keyboard navigation, and homepage gallery.
* Existing compass design download control passed a regression check.
* JavaScript syntax validated with node --check; stylesheet parsed without errors.
* Local static site build succeeded. Tests used dummy images; actual photos were NOT modified.

This is an upload package only. It is NOT a live/published change until you commit it.
