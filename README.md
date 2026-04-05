# JobHunter

Personal job feed + tracker — Data Analyst / BA / related roles across Bangalore, Pune, Hyderabad, Chennai, Mumbai.

## Files

```
jobhunter/
├── fetch_jobs.py                    ← run this to pull live jobs
├── docs/
│   ├── index.html                   ← the entire app (open in browser)
│   └── jobs.json                    ← job data (updated by the script)
└── .github/workflows/fetch.yml      ← auto-runs 3x daily on GitHub
```

---

## Deploy to GitHub Pages — 6 steps

### Step 1 — Get free Adzuna API keys
1. Go to **https://developer.adzuna.com**
2. Register a free account
3. Click **My Apps → Create new app**
4. Copy your **App ID** and **App Key**

### Step 2 — Create a GitHub repository
1. Go to **https://github.com** → sign in
2. Click **+** (top right) → **New repository**
3. Name it `jobhunter`, set to **Private**, click **Create repository**

### Step 3 — Upload files
On your new repo page, click **uploading an existing file**, then drag and drop:
- `fetch_jobs.py`
- `docs/index.html`
- `docs/jobs.json`
- `.github/workflows/fetch.yml`

Click **Commit changes**.

### Step 4 — Add API keys as GitHub Secrets
1. In your repo go to **Settings → Secrets and variables → Actions**
2. Click **New repository secret** and add:

| Name | Value |
|---|---|
| `ADZUNA_APP_ID` | Your Adzuna App ID |
| `ADZUNA_APP_KEY` | Your Adzuna App Key |
| `ANTHROPIC_API_KEY` | Your Claude key (optional) |

### Step 5 — Enable GitHub Pages
1. In your repo go to **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` · Folder: `/docs`
4. Click **Save**
5. Your app is live at `https://YOUR_USERNAME.github.io/jobhunter`

### Step 6 — Trigger first job fetch
1. In your repo go to **Actions** tab
2. Click **Fetch jobs** → **Run workflow** → **Run workflow**
3. Wait ~2 minutes, then refresh your GitHub Pages URL

Jobs auto-fetch at 8am, 2pm, 8pm IST every day after this.

---

## Run locally

```bash
pip install requests anthropic

export ADZUNA_APP_ID="your-id"
export ADZUNA_APP_KEY="your-key"
# optional:
export ANTHROPIC_API_KEY="sk-ant-..."

python fetch_jobs.py
# then open docs/index.html in your browser
```

## Customise

- **Roles** → edit `ROLES` list in `fetch_jobs.py`
- **Cities** → edit `CITIES` list in `fetch_jobs.py`
- **Frequency** → edit cron lines in `.github/workflows/fetch.yml`
