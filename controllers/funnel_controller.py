from services.funnel_service import FunnelService


class FunnelController:
    def __init__(self, funnel_service=None):
        self.funnel_service = funnel_service or FunnelService()

    def increment_stat(self, key, delta=1):
        return self.funnel_service.increment_stat(key, delta)
