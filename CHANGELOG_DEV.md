# CHANGELOG_DEV

## 2026-04-12

### Summary
- Performed a manual rollback to restore the stable MVP before the recent redirect / Telegram landing / price experiment wave.

### Files changed
- `app.py`
- `services/notification_service.py`
- `CURRENT_STATE.md`
- `CHANGELOG_DEV.md`

### Behavior changed
- Removed Telegram-to-family landing flow from the main app path.
- Removed family-page / best-offer marketplace rendering introduced in the unstable wave.
- Restored simpler direct offer opening behavior in the UI.
- Restored Telegram alert links to direct offer URLs.
- Removed noisy score / explanation / deal-pressure UI blocks added in the same wave.

### Rollback notes
- Rollback was done manually because git history does not contain the full experimental wave as clean commits.
- Preference was given to removing unstable layers instead of preserving partial redirect logic.

### Risk
- Internal family / ranking helper modules still exist in the codebase, but the unstable routing path is no longer active in the main user flow.
- Further cleanup can be done later, but stability was prioritized first.

### Status
- Stable rollback baseline restored.
