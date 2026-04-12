# QA Baseline Checklist

## Purpose
This checklist validates the current production-ready baseline of the alert notification system.
Focus areas:
- signal quality
- correct silence when no notification should be sent
- duplicate protection on repeated scans

## Preconditions
- A test user exists.
- The test user has a saved Telegram chat ID.
- Marketplace data is available and searchable.
- Manual trigger works from `Admin Panel` or `Profile`.
- Scan entrypoint is available:
  - manual: `run_alert_match_scan.py`
  - scheduled: `run_scheduled_alert_match_scan.py`

## Manual QA scenarios

### AirPods Pro without target price
- Setup: alert query = `AirPods Pro`
- Expected: relevant matches found

### AirPods without target price
- Setup: alert query = `AirPods`
- Expected: brand-level matches found

### Nike with target_price = 119 when product price is 120
- Setup: alert query = `Nike`, target price = `119`
- Expected: no notification

### Nike with target_price = 120
- Setup: alert query = `Nike`, target price = `120`
- Expected: notification sent

### Nike with target_price = 121
- Setup: alert query = `Nike`, target price = `121`
- Expected: notification sent

### MacBook when no matching products exist
- Setup: alert query = `MacBook`
- Expected: silence / no notification

### Run the same scan twice
- Setup: keep the same matching alerts and products
- Expected:
  - first run sends notifications
  - second run does not send duplicates

### Short alert: Pro
- Setup: alert query = `Pro`
- Expected: no notification
- Note: current matcher protects against weak short alerts

### Partial alert: Sneak
- Setup: alert query = `Sneak`
- Expected: no notification for `Sneakers`
- Note: current matcher does not match partial word fragments

### Mixed set
- Setup:
  - `AirPods`
  - `Nike` with target price `119`
  - `Pro`
  - `MacBook`
- Expected:
  - `AirPods` matches
  - `Nike(119)` stays silent
  - `Pro` stays silent
  - `MacBook` stays silent

## What to record after each run
- `users_processed`
- `matches_found`
- `notifications_sent`
- which alerts triggered
- whether false positives appeared

## Baseline acceptance criteria
Good baseline:
- no duplicate notifications on second run
- no notifications above target price
- no notifications when no match exists
- phrase alerts behave predictably

Known limitation:
- matching is stricter now, but still token-based rather than semantic

## Final assessment
This baseline is production-ready for controlled use.
Signal silence works well for no-match and target-price cases.
Matching is normalized and token-based, which reduces broad false positives.

## Batch QA

See:
- [Batch QA Note](BATCH_QA_NOTE.md)
