# Portfolio site

- `site/` is the public website. Netlify publishes only this folder.
- Your share counts and cash live in the **PORTFOLIO_JSON** GitHub secret, never in the files.
- `.github/workflows/update-prices.yml` runs every weekday evening: it fetches closing prices (Yahoo Finance via `yfinance`),
  recalculates weights, and commits `site/data/live.json` (prices and percentages only).
- The site reads that file straight from GitHub, and `netlify.toml` tells Netlify to skip deploys that only change it.
  Nightly prices cost 0 Netlify credits; only design, report or holdings changes deploy (15 credits each).

Full step-by-step setup is in the Portfolio Site Launch Guide. Short version:
1. Create a **public** GitHub repo named exactly `portfolio-site` and upload everything (show hidden files first on a Mac: Cmd+Shift+.).
2. Settings → Secrets and variables → Actions → New repository secret: name `PORTFOLIO_JSON`, value = your holdings
   in the format of `portfolio.example.json`.
3. Settings → Actions → General → Workflow permissions → Read and write.
4. In `site/feed.js`, replace `YOUR-GITHUB-USERNAME` with your GitHub username.
5. Actions → Update prices → Run workflow, and check `site/data/live.json` updates.
6. Netlify → Add new site → Import from GitHub → pick the repo → Deploy. Then add your domain.
