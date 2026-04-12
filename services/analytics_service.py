from database import get_admin_analytics, get_funnel_stats


class AnalyticsService:
    def _rate(self, start_value, end_value):
        if float(start_value) <= 0:
            return 0.0
        return round((float(end_value) / float(start_value)) * 100, 1)

    def _drop_off(self, start_value, end_value):
        if float(start_value) <= 0:
            return 0.0
        return round((1 - (float(end_value) / float(start_value))) * 100, 1)

    def _build_funnel_steps(self, funnel_stats):
        visits = int(funnel_stats.get("visits", 0))
        find_cheaper_clicks = int(funnel_stats.get("find_cheaper_clicks", 0))
        get_deal_clicks = int(funnel_stats.get("get_deal_clicks", 0))
        completed_deals = int(funnel_stats.get("completed_deals", 0))

        return [
            {
                "key": "visits",
                "label": "Visits",
                "value": visits,
            },
            {
                "key": "find_cheaper_clicks",
                "label": "Clicked Find Cheaper",
                "value": find_cheaper_clicks,
            },
            {
                "key": "get_deal_clicks",
                "label": "Clicked Get Deal",
                "value": get_deal_clicks,
            },
            {
                "key": "completed_deals",
                "label": "Completed Deals",
                "value": completed_deals,
            },
        ]

    def _build_funnel_transitions(self, funnel_steps):
        transitions = []
        for index in range(len(funnel_steps) - 1):
            current_step = funnel_steps[index]
            next_step = funnel_steps[index + 1]
            transitions.append(
                {
                    "label": f"{current_step['label']} -> {next_step['label']}",
                    "from_key": current_step["key"],
                    "to_key": next_step["key"],
                    "from_value": current_step["value"],
                    "to_value": next_step["value"],
                    "conversion_rate": self._rate(
                        current_step["value"],
                        next_step["value"],
                    ),
                    "drop_off_rate": self._drop_off(
                        current_step["value"],
                        next_step["value"],
                    ),
                }
            )
        return transitions

    def _build_funnel_summary(self, funnel_stats):
        funnel_steps = self._build_funnel_steps(funnel_stats)
        transitions = self._build_funnel_transitions(funnel_steps)
        worst_transition = None
        if transitions:
            worst_transition = max(
                transitions,
                key=lambda transition: transition["drop_off_rate"],
            )

        return {
            "steps": funnel_steps,
            "transitions": transitions,
            "worst_transition": worst_transition,
        }

    def get_admin_dashboard_analytics(self):
        overview = get_admin_analytics()
        funnel_stats = get_funnel_stats()
        funnel = self._build_funnel_summary(funnel_stats)

        return {
            "ok": True,
            "message": "Analytics loaded.",
            "overview": overview,
            "funnel": funnel,
        }
