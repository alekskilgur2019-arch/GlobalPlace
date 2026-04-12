from services.user_profile_service import UserProfileService


class UserProfileController:
    def __init__(self, user_profile_service=None):
        self.user_profile_service = user_profile_service or UserProfileService()

    def add_search_preference(self, user_id, query):
        return self.user_profile_service.add_search_preference(user_id, query)

    def get_preferences(self, user_id):
        return self.user_profile_service.get_preferences(user_id)

    def get_behavior(self, user_id):
        return self.user_profile_service.get_behavior(user_id)

    def save_telegram_chat_id(self, user_id, telegram_chat_id):
        return self.user_profile_service.save_telegram_chat_id(user_id, telegram_chat_id)

    def get_telegram_chat_id(self, user_id):
        return self.user_profile_service.get_telegram_chat_id(user_id)

    def get_telegram_connection_status(self, user_id):
        return self.user_profile_service.get_telegram_connection_status(user_id)

    def get_or_create_telegram_connect_link(self, user_id):
        return self.user_profile_service.get_or_create_telegram_connect_link(user_id)

    def get_seller_access_status(self, user_id):
        return self.user_profile_service.get_seller_access_status(user_id)

    def send_telegram_test_message(self, user_id):
        return self.user_profile_service.send_telegram_test_message(user_id)

    def link_telegram_chat_by_connect_token(self, connect_token, telegram_chat_id):
        return self.user_profile_service.link_telegram_chat_by_connect_token(
            connect_token, telegram_chat_id
        )
