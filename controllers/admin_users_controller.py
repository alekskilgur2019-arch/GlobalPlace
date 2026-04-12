from services.admin_users_service import AdminUsersService


class AdminUsersController:
    def __init__(self, admin_users_service=None):
        self.admin_users_service = admin_users_service or AdminUsersService()

    def get_users(self):
        return self.admin_users_service.list_users()

    def promote_user(self, acting_admin_user_id, target_user_id):
        return self.admin_users_service.promote_user(
            acting_admin_user_id=acting_admin_user_id,
            target_user_id=target_user_id,
        )

    def delete_user(self, acting_admin_user_id, target_user_id):
        return self.admin_users_service.delete_user(
            acting_admin_user_id=acting_admin_user_id,
            target_user_id=target_user_id,
        )
