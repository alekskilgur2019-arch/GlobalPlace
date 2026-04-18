# CURRENT_STATE

## Status
- Rollback completed.
- Current target: restored stable MVP before redirect / Telegram landing / price experiment wave.

## Rollback target
- Remove unstable redirect and offer-open experiments.
- Remove Telegram landing routing introduced for the broken flow.
- Remove noisy price / score / explanation UI added in the same unstable wave.
- Keep the simpler working MVP behavior for auth, search, alerts, and Telegram notifications.

## Files reverted
- `app.py`
- `services/notification_service.py`

## Restored stable behavior
- App loads normally without redirect interception.
- Marketplace renders normal search results instead of family landing routing.
- `Open` uses the simpler direct offer flow again.
- Telegram alert messages point to direct offer URLs again.
- No intermediate redirect machinery remains in the main app flow.
- No noisy score / explanation layer remains in the deal UI.

## Notes
- Git history is insufficient for a clean commit-level revert, so rollback was done by code inspection.
- Stability was prioritized over preserving experimental layers.

## N8N Archive Note
- Date: `2026-04-14`
- Archived workflows:
  - `AI Rig — Health Check`
  - `AI Rig — FFmpeg Render Job`
  - `AI Rig — FFmpeg Self Test`
  - `Master Shorts Pipeline — AI Rig + Metadata`
  - `Master Shorts Pipeline — AI Rig + Metadata + Notify`
  - `AI Rig — Video Agent Contour`
  - `AI Rig — Video Agent Render Job`
  - `AI Rig — Video Agent Metadata`
- Kept active:
  - `Master Shorts Pipeline — AI Rig`
- Archive method:
  - `isArchived = 1` in local `n8n` database
  - no workflow was deleted
