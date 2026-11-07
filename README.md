# Discipline Bot -- Phase 2-6 (routine tracking, additional activities, journal, expenses)

This is the first working slice of the full system: daily routine
reminders with Completed/Not Completed buttons, additional-activity
logging, the 10:11 PM journal (trading + daily), and expense tracking
-- all saved to one Google Sheet. The Excel workbook + dashboard and
the weekly/monthly reports (Phase 7-9 in the master plan) come next,
once this slice is confirmed working.

## How it runs for free

GitHub Actions has no "stay open and listen" mode -- it only runs on a
schedule. So instead of a live webhook, `poller.py` runs every 5
minutes, asks Telegram "anything new since last time?", processes it,
and checks whether any routine reminder is due. This keeps everything
in one language (Python) and avoids a second platform, at the cost of
up to a ~5-minute delay before a button tap or reply is acknowledged.

Running every 5 minutes, all day, uses more Actions minutes than the
2,000/month private-repo free allowance -- so **this repo needs to be
public** to get unlimited free minutes. That's safe here: your actual
data (routine, journal, trades, expenses) lives in your private Google
Sheet, never in the repo. The code itself has no personal content in
it beyond generic task labels.

## One-time setup

1. **Create the Telegram bot**
   Message [@BotFather](https://t.me/BotFather) on Telegram, send
   `/newbot`, follow the prompts. Save the token it gives you.

2. **Get your chat ID**
   Send any message to your new bot, then visit
   `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` in a browser
   and read `message.chat.id` from the JSON. (Or message
   [@userinfobot](https://t.me/userinfobot) to get your own ID.)

3. **Create a Google Cloud service account**
   - In the [Google Cloud Console](https://console.cloud.google.com/),
     create a project, enable the **Google Sheets API**.
   - Create a service account, then a JSON key for it -- download the
     key file.
   - Base64-encode the whole JSON file (so it can go in a GitHub
     Secret as one line):
     `base64 -w0 service-account.json` (Linux/Mac) or
     `certutil -encode service-account.json out.b64` (Windows, then
     strip the header/footer lines).

4. **Create the Google Sheet**
   Make a new, empty Google Sheet. Share it with the service account's
   email address (found in the JSON key, looks like
   `...@...iam.gserviceaccount.com`) as **Editor**. Copy the Sheet ID
   from its URL: `https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit`.

5. **Push this code to a public GitHub repo**, then add these four
   repository secrets (Settings -> Secrets and variables -> Actions):
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `GOOGLE_SERVICE_ACCOUNT_JSON_B64`
   - `GOOGLE_SHEET_ID`

6. **Test it**
   Go to the Actions tab, run "Discipline bot poller" manually
   (`workflow_dispatch`). It should create all the tabs in your Sheet
   on first run. Then let the 5-minute schedule take over -- no laptop,
   no VS Code needed after this.

## Local testing (optional)

```bash
export TELEGRAM_BOT_TOKEN=...
export TELEGRAM_CHAT_ID=...
export GOOGLE_SERVICE_ACCOUNT_JSON_B64=...
export GOOGLE_SHEET_ID=...
pip install -r requirements.txt
python poller.py
```

## What's intentionally simplified in this first version

- "Completed" logs instantly; "Not completed" always asks for a reason
  (as required), but there's no optional note on a Completed tap yet.
- No "correct a past entry" or "view history" commands yet.
- `/addactivity` and `/expense` work as typed commands any time; there's
  no Telegram menu button for them yet.

None of this is hard to add -- just scoped out of v1 to ship something
testable first, matching the project's own phase-by-phase plan.
