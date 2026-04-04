"""Unit tests for ELK shipper."""

from unittest.mock import MagicMock, patch

import pytest

from inferwall.core.elk_shipper import ElkShipper


class TestElkShipper:
    def test_disabled_when_no_url(self):
        shipper = ElkShipper(endpoint=None)
        assert not shipper.enabled

    def test_enabled_with_url(self):
        shipper = ElkShipper(endpoint="http://localhost:8080")
        assert shipper.enabled

    @patch("inferwall.core.elk_shipper.httpx.post")
    def test_ship_sync_posts_json(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        shipper = ElkShipper(endpoint="http://localhost:8080")
        shipper.ship_sync({"log_type": "scan", "decision": "block"})
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        assert kwargs["json"]["decision"] == "block"

    @patch("inferwall.core.elk_shipper.httpx.post")
    def test_ship_sync_silently_fails(self, mock_post):
        mock_post.side_effect = Exception("connection refused")
        shipper = ElkShipper(endpoint="http://localhost:8080")
        # Should not raise
        shipper.ship_sync({"log_type": "scan"})
