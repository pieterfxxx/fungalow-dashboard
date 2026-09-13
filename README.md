# Fungalow Dashboard

Automated weather dashboard. GitHub Actions rebuilds and publishes the dashboard every hour.

## GitHub setup

1. Add this repository's `TIDECHECK_API_KEY` as a GitHub Actions secret:
   **Settings → Secrets and variables → Actions → New repository secret**
2. Set:
   - Name: `TIDECHECK_API_KEY`
   - Value: your TideCheck API key
3. In **Settings → Pages**, choose **GitHub Actions** as the source if GitHub asks for a Pages source.
4. Run **Actions → Update Fungalow dashboard → Run workflow** once to test it.

The public Pages site contains only `dashboard.html` and the `static/` assets. The Python scripts and API key are not published as part of the Pages site.
