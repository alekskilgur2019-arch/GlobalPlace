from services.auth_service import AuthService


class AuthController:
    def __init__(self, auth_service=None):
        self.auth_service = auth_service or AuthService()

    def login(self, username, password):
        return self.auth_service.login(username, password)

    def register(self, username, password):
        return self.auth_service.register(username, password)
