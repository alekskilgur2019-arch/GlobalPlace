from database import increment_funnel_stat


class FunnelService:
    def increment_stat(self, key, delta=1):
        normalized_key = str(key or "").strip()
        if not normalized_key:
            return {
                "ok": False,
                "message": "Stat key is required.",
            }

        increment_funnel_stat(normalized_key, delta)
        return {
            "ok": True,
            "message": "Stat updated.",
        }
