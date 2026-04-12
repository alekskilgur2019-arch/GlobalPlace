# Alert Scan Ops

## Manual triggers
- Admin UI: open `Admin Panel` and click `Run Telegram alert scan`.
- Profile UI: open `Profile` and click `Run Telegram alert check`.
- Manual script:
```bash
.venv/bin/python run_alert_match_scan.py
```

## Scheduled entrypoint
Use the scheduled entrypoint for external cron-style execution:
```bash
.venv/bin/python run_scheduled_alert_match_scan.py
```

It prints structured JSON with:
- `auto_scan_enabled`
- `scan_interval_minutes`
- `skipped`
- `users_processed`
- `matches_found`
- `notifications_sent`
- `message`

## Cron example
Example cron entry for every 15 minutes:
```cron
*/15 * * * * cd /Users/aleksandr/Desktop/GlobalPlace && ./.venv/bin/python run_scheduled_alert_match_scan.py >> /tmp/globalplace_alert_scan.log 2>&1
```

## Execution settings
- `auto_scan_enabled`
  Controls whether the scheduled entrypoint actually runs the scan.
  If `false`, scheduled execution exits cleanly with `skipped: true`.
- `scan_interval_minutes`
  Stores the intended scan cadence for operators and future cron alignment.
  It does not create an internal scheduler.

## Scheduled run statuses
- `success`
  Scheduled entrypoint ran and completed the scan flow.
- `skipped`
  Scheduled entrypoint did not run because `auto_scan_enabled` is disabled.
- `failed`
  Scheduled entrypoint started but ended with an error.

## Where admins can see status
In `Admin Panel`:
- `Notification policy`
- `Alert scan execution`
- `Scheduled scan status`

The `Scheduled scan status` block shows:
- last scheduled run time
- last scheduled run status
- last users processed
- last matches found
- last notifications sent
- last error message, if any

## Troubleshooting
- No notifications sent:
  Check that users have `telegram_chat_id` saved and alerts exactly match product names.
- Scheduled run is always skipped:
  Enable `auto_scan_enabled` in `Admin Panel`.
- Scheduled run works but sends nothing:
  Check target price conditions, anti-duplicate protection, and cooldown policy.
- Telegram issues:
  Verify `.env` has a valid `TELEGRAM_BOT_TOKEN`.
