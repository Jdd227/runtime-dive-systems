# Dive Current V1.2 — Tides first

Update for `Jdd227/dive-current` GitHub Pages deployment.

## Priorities

1. **NOAA Tides** is now the first, most prominent right-hand panel. It has a wider chart (48-hour detailed view), 14-day NOAA prediction cache request, high/low event display where provided by NOAA, and a date picker with previous/next-day controls. Graph clicks and the map tide slider change the selected time.
2. **Currents** retain two explicit display modes: arrows (locally interpolated within sampled NOAA wet cells for visual density) and flowing particles (moving faster on screen for visibility; animation speed is *not* the ocean current speed). Current frame cache limits repeated downloads during scrubbing. Selected model valid-time is visible.
3. **Forecast horizon**: the NOAA source advertises up to 72 hours for SSCOFS, but specific OPeNDAP NetCDF files might be missing. The updater *requests* a larger set through f072, publishes only validated frames, and does not substitute fake currents. Outside verified frames, currents are unavailable; tides remain selectable.
4. **Tide-cache bug**: previous `stations.json` had `generated_at: null`, causing `AttributeError` in the update script before any NOAA request. V1.2 handles this and retains fallback NOAA tide station IDs. It does not invent tide values.
5. **Existing map, bathymetry and routing** remain on the working V1.1 implementation. Depth markers remain marine DNR CoNED only.

## Upload

Unzip and upload **only** these replacement files to the existing GitHub repository, matching their paths:

- `docs/index.html`
- `docs/dive-current.css`
- `docs/dive-current.js`
- `scripts/update_tides.py`
- `scripts/update_sscofs.py`
- `tests/test_v11_regressions.py` (updates previous stride expectation)
- `tests/test_v12.py` (new checks)
- `tests/test_tide_recovery.py` (new cache recovery regression)
- `tests/test_render_modes.cjs` (optional Node-based isolated visual renderer test)

**Do not upload or delete** `docs/data/`; GitHub Actions owns it and holds the latest NOAA data and timestamps. Leave `.github/workflows/deploy-pages.yml` and Pages settings unchanged.

Committing the files to `main` should trigger the existing workflow. Check `Actions > Dive Current · NOAA data and GitHub Pages > build`. The NOAA processor may log skipped fXXX files on intermittent upstream HTTP 502. That is expected and the manifest includes only validated frames.

### Validation

- `node --check docs/dive-current.js`
- `python -m unittest discover -s tests -v`
- `node tests/test_render_modes.cjs`
- Browser layout inspected at desktop and mobile sizes with JavaScript/network map data disabled. **Actual NOAA services, coast bathymetry and animation on the published website have not yet been verified**.

The JS renderer labels display-grid arrows as locally interpolated NOAA model guidance, not additional observations or new model spatial resolution. Near-shore hazards, dive-depth currents, and navigation safety require independent verification.
