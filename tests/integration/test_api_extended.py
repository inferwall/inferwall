"""Extended API tests for M2-M4 endpoints."""

import os

import pytest
from fastapi.testclient import TestClient

from inferwall.api.app import app


@pytest.fixture
def client() -> TestClient:
    os.environ.pop("IW_API_KEY", None)
    os.environ.pop("IW_ADMIN_KEY", None)
    return TestClient(app)


class TestSignaturesCatalogAPI:
    def test_list_signatures(self, client: TestClient) -> None:
        response = client.get("/v1/signatures")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 108
        assert all("id" in sig for sig in data)

    def test_get_signature_by_id(self, client: TestClient) -> None:
        response = client.get("/v1/signatures/INJ-D-001")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "INJ-D-001"
        assert data["engine"] == "heuristic"
        assert data["severity"] == "high"

    def test_get_signature_not_found(self, client: TestClient) -> None:
        response = client.get("/v1/signatures/NONEXISTENT")
        assert response.status_code == 404


class TestSessionAPI:
    def test_create_session(self, client: TestClient) -> None:
        response = client.post(
            "/v1/sessions",
            json={"session_id": "test-sess-1"},
        )
        assert response.status_code == 201
        assert response.json()["status"] == "created"

    def test_get_session(self, client: TestClient) -> None:
        client.post(
            "/v1/sessions",
            json={"session_id": "test-sess-2"},
        )
        response = client.get("/v1/sessions/test-sess-2")
        assert response.status_code == 200
        data = response.json()
        assert data["cumulative_score"] == 0.0
        assert data["turn_count"] == 0

    def test_delete_session(self, client: TestClient) -> None:
        client.post(
            "/v1/sessions",
            json={"session_id": "test-sess-3"},
        )
        response = client.delete("/v1/sessions/test-sess-3")
        assert response.status_code == 200

    def test_get_nonexistent_session(self, client: TestClient) -> None:
        response = client.get("/v1/sessions/nonexistent")
        assert response.status_code == 404


class TestAnalyzeAPI:
    def test_analyze_input(self, client: TestClient) -> None:
        response = client.post(
            "/v1/analyze/input",
            json={"text": "What is the weather?"},
        )
        assert response.status_code == 200
        assert response.json()["decision"] == "allow"

    def test_analyze_output(self, client: TestClient) -> None:
        response = client.post(
            "/v1/analyze/output",
            json={"text": "The answer is 42."},
        )
        assert response.status_code == 200


class TestAuthAPI:
    def test_login_dev_mode(self, client: TestClient) -> None:
        response = client.post(
            "/v1/auth/login",
            json={"key": "anything"},
        )
        assert response.status_code == 200
        assert response.json()["mode"] == "dev"

    def test_logout(self, client: TestClient) -> None:
        response = client.post("/v1/auth/logout")
        assert response.status_code == 200

    def test_check_dev_mode(self, client: TestClient) -> None:
        response = client.get("/v1/auth/check")
        assert response.status_code == 200


class TestConfigAPI:
    def test_get_config(self, client: TestClient) -> None:
        response = client.get("/v1/config")
        assert response.status_code == 200
        data = response.json()
        assert "tls_mode" in data
        assert "auth_enabled" in data


class TestAdminAPI:
    def test_reload(self, client: TestClient) -> None:
        response = client.post("/v1/admin/reload")
        assert response.status_code == 200
        assert response.json()["status"] == "reloaded"

    def test_stats(self, client: TestClient) -> None:
        response = client.get("/v1/admin/stats")
        assert response.status_code == 200
        assert "signature_count" in response.json()


class TestPoliciesAPI:
    def test_list_policies(self, client: TestClient) -> None:
        response = client.get("/v1/policies")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["name"] == "default"
