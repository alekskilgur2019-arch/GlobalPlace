import hashlib

from database import create_user, get_user_by_username


class AuthService:
    def _hash_password(self, password):
        return hashlib.sha256(str(password).encode("utf-8")).hexdigest()

    def login(self, username, password):
        normalized_username = str(username or "").strip()
        if not normalized_username or not str(password or ""):
            return {
                "ok": False,
                "message": "Username and password are required.",
                "user": None,
            }

        user = get_user_by_username(normalized_username)
        if not user or user[2] != self._hash_password(password):
            return {
                "ok": False,
                "message": "Invalid username or password.",
                "user": None,
            }

        return {
            "ok": True,
            "message": "Login successful.",
            "user": {
                "id": user[0],
                "username": user[1],
                "role": user[3] or "user",
            },
        }

    def register(self, username, password):
        normalized_username = str(username or "").strip()
        if not normalized_username or not str(password or ""):
            return {
                "ok": False,
                "message": "Username and password are required.",
            }

        try:
            create_user(normalized_username, self._hash_password(password))
            return {
                "ok": True,
                "message": "Registration successful.",
            }
        except Exception:
            return {
                "ok": False,
                "message": "User already exists.",
            }
