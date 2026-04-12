import hashlib

from database import (
    clear_admin_roles,
    create_user,
    get_user_by_username,
    set_user_password,
    set_user_role,
)


class GlobalAdminService:
    def _hash_password(self, password):
        return hashlib.sha256(str(password).encode("utf-8")).hexdigest()

    def ensure_global_admin(self, username, password):
        normalized_username = str(username or "").strip()
        normalized_password = str(password or "")

        if not normalized_username:
            return {
                "ok": False,
                "message": "Username is required.",
            }

        if not normalized_password:
            return {
                "ok": False,
                "message": "Password is required.",
            }

        hashed_password = self._hash_password(normalized_password)
        existing_user = get_user_by_username(normalized_username)

        clear_admin_roles(except_username=normalized_username)

        if existing_user:
            set_user_password(normalized_username, hashed_password)
            set_user_role(normalized_username, "admin")
            return {
                "ok": True,
                "message": "Existing user updated as global admin.",
                "username": normalized_username,
                "created": False,
                "role": "admin",
            }

        create_user(normalized_username, hashed_password)
        set_user_role(normalized_username, "admin")
        return {
            "ok": True,
            "message": "Global admin user created.",
            "username": normalized_username,
            "created": True,
            "role": "admin",
        }
