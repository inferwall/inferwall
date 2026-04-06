"""Unit tests for ELK shipper."""

import os
from unittest.mock import MagicMock, patch

from inferwall.plugins.siem.elk_shipper import ElkShipper


class TestElkShipper:
    def test_disabled_when_no_url(self):
        shipper = ElkShipper(endpoint=None)
        assert not shipper.enabled

    def test_enabled_with_url(self):
        shipper = ElkShipper(endpoint="http://localhost:8080")
        assert shipper.enabled

    @patch("inferwall.plugins.siem.elk_shipper.httpx.post")
    def test_ship_sync_posts_json(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        shipper = ElkShipper(endpoint="http://localhost:8080")
        shipper.ship_sync({"log_type": "scan", "decision": "block"})
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        assert kwargs["json"]["decision"] == "block"

    @patch("inferwall.plugins.siem.elk_shipper.httpx.post")
    def test_ship_sync_silently_fails(self, mock_post):
        mock_post.side_effect = Exception("connection refused")
        shipper = ElkShipper(endpoint="http://localhost:8080")
        # Should not raise
        shipper.ship_sync({"log_type": "scan"})


class TestCreateShipper:
    """Tests for plugin initialization."""

    def test_returns_none_when_no_env_var(self):
        """create_shipper() returns None when IW_ELK_URL is not set."""
        # Ensure env var is not set
        old_value = os.environ.pop("IW_ELK_URL", None)
        try:
            from inferwall.plugins.siem import create_shipper

            result = create_shipper()
            assert result is None
        finally:
            # Restore env var if it was set
            if old_value is not None:
                os.environ["IW_ELK_URL"] = old_value

    def test_returns_shipper_when_env_var_set(self):
        """create_shipper() returns shipper when IW_ELK_URL is set."""
        old_value = os.environ.get("IW_ELK_URL")
        try:
            os.environ["IW_ELK_URL"] = "http://localhost:8080"
            from inferwall.plugins.siem import create_shipper

            result = create_shipper()
            assert result is not None
            assert result.enabled
        finally:
            if old_value is not None:
                os.environ["IW_ELK_URL"] = old_value
            else:
                os.environ.pop("IW_ELK_URL", None)

    def test_returns_none_when_explicitly_disabled(self):
        """create_shipper() returns None when endpoint is explicitly None."""
        from inferwall.plugins.siem import create_shipper

        result = create_shipper(endpoint=None)
        assert result is None
