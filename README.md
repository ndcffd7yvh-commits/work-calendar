# Calendar Sync

Automatically syncs planning from Dropbox to an `.ics` file that your iPhone can subscribe to.

## How it works

Every morning at 7:00 AM (Brussels time), GitHub Actions:
1. Downloads `planning_2026.xlsx` from your Dropbox
2. Extracts Abdel's schedule
3. Generates `output/abdel.ics`
4. Commits it back to this repo

Your iPhone subscribes to the raw URL of that file and refreshes automatically.

---

## Setup (one time)

### 1. Add your Dropbox token as a GitHub Secret

- Go to your repo → **Settings** → **Secrets and variables** → **Actions**
- Click **New repository secret**
- Name: `DROPBOX_TOKEN`
- Value: your Dropbox access token
- Click **Add secret**

### 2. Enable GitHub Pages

- Go to your repo → **Settings** → **Pages**
- Source: **Deploy from a branch**
- Branch: `main`, folder: `/ (root)`
- Click **Save**

### 3. Run the workflow once manually

- Go to **Actions** → **Generate Abdel Calendar** → **Run workflow**
- Wait ~30 seconds for it to finish
- Check that `output/abdel.ics` appeared in your repo

### 4. Get the calendar URL

Your `.ics` URL will be:
```
https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO_NAME/main/output/abdel.ics
```

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub username and repo name.

### 5. Subscribe on iPhone

- Open **Settings** → **Calendar** → **Accounts** → **Add Account** → **Other**
- Tap **Add Subscribed Calendar**
- Paste the URL above
- Tap **Next** → **Save**

Done! Your iPhone will now refresh Abdel's calendar automatically.

---

## Refresh frequency

The workflow runs **daily at 7 AM Brussels time**. iOS refreshes subscribed calendars roughly every few hours on its own schedule.

If you need to force a refresh: go to **Actions** → **Generate Abdel Calendar** → **Run workflow**.
