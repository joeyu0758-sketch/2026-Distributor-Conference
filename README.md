# Maxxis 2026 Distributor Conference

Conference website: a spinning 3D MAXXIS wordmark intro, a photo wheel, the Archives layers and the ride deck.

Static site, no build step. `index.html` is the page, photos are in `img/`. Hosted with GitHub Pages from the `main` branch.

## Updating

The Claude version is the master copy. After changing it, save that page's HTML and run:

    python3 tools/build_from_claude.py <claude-page.html>

then commit and push. GitHub Pages republishes within a minute or two.
