# Batch QA Note

## Purpose
This note helps interpret batch alert QA runs.

## What the script does
`run_batch_alert_qa.py` runs multiple alerts and evaluates signal quality for the current alert notification baseline.

## Expected output interpretation

### A. Good behavior
- strong alerts trigger notifications
- weak alerts such as `Pro`, `Max`, `Air`, `PS` do not trigger
- `target_price` filtering works
- second run produces zero notifications because anti-duplicate protection blocks repeats

### B. Warning signs
- too many notifications: matcher may be too loose
- weak alerts trigger: matcher regression
- valid alerts do not trigger: possible false negative
- inconsistent results between runs: investigate state or test setup

### C. Key metrics meaning
- `users_processed`: how many users were evaluated in the scan
- `matches_found`: how many alert-product matches were detected
- `notifications_sent`: how many Telegram notifications were actually sent

### D. Decision guidance
- if results match expectations: no change needed
- if weak alerts trigger: investigate matcher behavior
- if strong alerts fail: investigate matching rules or dataset quality

### E. What to check manually
- which alerts actually triggered notifications
- which alerts were ignored
- whether any weak alerts produced signals
- whether expected strong alerts were missing

Focus on signal quality, not quantity.
