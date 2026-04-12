import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import database
from services.alert_service import AlertService
from services.events import log_event
from services.metrics import (
    get_click_rate,
    get_engagement_score,
    get_event_counts,
    get_open_rate,
)
from services.notification_service import NotificationService
from services.product_service import ProductService


class EventsMetricsTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_db_path = database.DB_PATH
        database.DB_PATH = str(Path(self.temp_dir.name) / "test_database.db")
        database.init_db()

    def tearDown(self):
        database.DB_PATH = self.old_db_path
        self.temp_dir.cleanup()

    def _create_user(self, username="events_user"):
        hashed_password = hashlib.sha256(b"password").hexdigest()
        user_id = database.create_user(username, hashed_password)
        return user_id

    def test_valid_event_logging(self):
        user_id = self._create_user()
        log_event(user_id, "product_viewed", "MacBook Pro M1", offer_id=10, price=999.0)

        counts = get_event_counts(user_id, "MacBook Pro M1")
        self.assertEqual(counts["product_viewed"], 1)

    def test_invalid_event_type_raises_error(self):
        user_id = self._create_user()
        with self.assertRaises(ValueError):
            log_event(user_id, "invalid_event", "MacBook Pro M1")

    def test_event_counts_aggregation(self):
        user_id = self._create_user()
        log_event(user_id, "notification_sent", "MacBook Pro M1")
        log_event(user_id, "notification_opened", "MacBook Pro M1")
        log_event(user_id, "offer_clicked", "MacBook Pro M1", offer_id=101, price=999.0)
        log_event(user_id, "offer_clicked", "MacBook Pro M1", offer_id=101, price=999.0)

        counts = get_event_counts(user_id, "MacBook Pro M1")
        self.assertEqual(counts["notification_sent"], 1)
        self.assertEqual(counts["notification_opened"], 1)
        self.assertEqual(counts["offer_clicked"], 2)

    def test_safe_open_rate_with_zero_sent(self):
        user_id = self._create_user()
        self.assertEqual(get_open_rate(user_id, "MacBook Pro M1"), 0.0)

    def test_safe_click_rate_with_zero_opened(self):
        user_id = self._create_user()
        log_event(user_id, "notification_sent", "MacBook Pro M1")
        self.assertEqual(get_click_rate(user_id, "MacBook Pro M1"), 0.0)

    def test_engagement_score_formula(self):
        user_id = self._create_user()
        log_event(user_id, "notification_opened", "MacBook Pro M1")
        log_event(user_id, "product_viewed", "MacBook Pro M1")
        log_event(user_id, "offer_clicked", "MacBook Pro M1", offer_id=101, price=999.0)
        log_event(user_id, "offer_clicked", "MacBook Pro M1", offer_id=102, price=998.0)

        self.assertEqual(get_engagement_score(user_id, "MacBook Pro M1"), 8)

    def test_notification_sent_logged_only_after_successful_send(self):
        user_id = self._create_user("notify_user")
        database.set_user_telegram_chat_id(user_id, "123456")
        AlertService().create_user_alert(user_id, "MacBook Pro M1")
        ProductService().create_product(
            name="MacBook Pro M1",
            price=999,
            original_price=1100,
            source="eBay",
            url="https://www.ebay.com/itm/123456789012",
            condition="New",
        )

        with patch("services.notification_service.send_alert_match", return_value=False):
            NotificationService().notify_alert_matching_deals()
        counts_after_failed_send = get_event_counts(user_id, "MacBook Pro M1")
        self.assertEqual(counts_after_failed_send["notification_sent"], 0)

        with patch("services.notification_service.send_alert_match", return_value=True):
            NotificationService().notify_alert_matching_deals()
        counts_after_successful_send = get_event_counts(user_id, "MacBook Pro M1")
        self.assertEqual(counts_after_successful_send["notification_sent"], 1)


if __name__ == "__main__":
    unittest.main()
