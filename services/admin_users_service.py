from database import delete_user, get_all_users, promote_user_to_admin


class AdminUsersService:
    def _validate_user_id(self, user_id, field_name="User id"):
        if user_id is None:
            return {
                "ok": False,
                "message": f"{field_name} is required.",
            }

        try:
            normalized_user_id = int(user_id)
        except (TypeError, ValueError):
            return {
                "ok": False,
                "message": f"{field_name} must be a valid integer.",
            }

        if normalized_user_id <= 0:
            return {
                "ok": False,
                "message": f"{field_name} must be greater than 0.",
            }

        return {
            "ok": True,
            "user_id": normalized_user_id,
        }

    def _get_users_index(self):
        rows = get_all_users()
        users = [
            {
                "id": row[0],
                "username": row[1],
                "role": row[2],
                "created_at": row[3],
            }
            for row in rows
        ]
        users_by_id = {user["id"]: user for user in users}
        return users, users_by_id

    def _validate_admin_action(self, acting_admin_user_id, target_user_id):
        acting_validation = self._validate_user_id(
            acting_admin_user_id,
            field_name="Acting admin user id",
        )
        if not acting_validation["ok"]:
            return acting_validation

        target_validation = self._validate_user_id(
            target_user_id,
            field_name="Target user id",
        )
        if not target_validation["ok"]:
            return target_validation

        users, users_by_id = self._get_users_index()
        acting_user = users_by_id.get(acting_validation["user_id"])
        target_user = users_by_id.get(target_validation["user_id"])

        if not acting_user:
            return {
                "ok": False,
                "message": "Acting admin user not found.",
            }

        if acting_user["role"] != "admin":
            return {
                "ok": False,
                "message": "Only admin users can perform this action.",
            }

        if not target_user:
            return {
                "ok": False,
                "message": "Target user not found.",
            }

        return {
            "ok": True,
            "acting_user": acting_user,
            "target_user": target_user,
            "users": users,
        }

    def list_users(self):
        users, _ = self._get_users_index()
        return {
            "ok": True,
            "message": "Users loaded.",
            "users": users,
        }

    def promote_user(self, acting_admin_user_id, target_user_id):
        validation = self._validate_admin_action(acting_admin_user_id, target_user_id)
        if not validation["ok"]:
            return {
                "ok": False,
                "message": validation["message"],
            }

        target_user = validation["target_user"]
        if target_user["role"] == "admin":
            return {
                "ok": False,
                "message": "User is already an admin.",
            }

        updated_count = promote_user_to_admin(target_user["id"])
        if updated_count <= 0:
            return {
                "ok": False,
                "message": "Failed to promote user.",
            }

        return {
            "ok": True,
            "message": "User promoted to admin.",
            "user_id": target_user["id"],
        }

    def delete_user(self, acting_admin_user_id, target_user_id):
        validation = self._validate_admin_action(acting_admin_user_id, target_user_id)
        if not validation["ok"]:
            return {
                "ok": False,
                "message": validation["message"],
            }

        acting_user = validation["acting_user"]
        target_user = validation["target_user"]
        if target_user["role"] == "admin":
            return {
                "ok": False,
                "message": "Admin user cannot be deleted.",
            }

        if acting_user["id"] == target_user["id"]:
            return {
                "ok": False,
                "message": "Admin user cannot delete themselves.",
            }

        deleted_count = delete_user(target_user["id"])
        if deleted_count <= 0:
            return {
                "ok": False,
                "message": "Failed to delete user.",
            }

        return {
            "ok": True,
            "message": "User deleted.",
            "user_id": target_user["id"],
        }
