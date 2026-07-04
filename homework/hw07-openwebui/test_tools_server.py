import pytest
from unittest.mock import patch, Mock
import httpx
from tools_server import app

client = app.test_client()


class TestHealthEndpoint:
    def test_health_returns_ok(self):
        response = client.get("/health")
        assert response.status_code == 200

        data = response.get_json()
        assert data["status"] == "ok"
        assert data["server"] == "tools_server"

    def test_health_returns_json(self):
        response = client.get("/health")
        assert response.is_json

    def test_health_wrong_method(self):
        response = client.post("/health")
        assert response.status_code in [404, 405]


class TestCountryEndpoint:
    @patch("tools_server.RAPIDAPI_KEY", "fake_key")
    @patch("tools_server.httpx.get")
    def test_country_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "France", "iso2": "FR"},
            {"name": "Japan", "iso2": "JP"}
        ]
        mock_get.return_value = mock_response

        response = client.get("/country/France")
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert data["country"] == "France"
        assert data["data"]["name"] == "France"

    @patch("tools_server.RAPIDAPI_KEY", "fake_key")
    @patch("tools_server.httpx.get")
    def test_country_not_found(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "France", "iso2": "FR"}
        ]
        mock_get.return_value = mock_response

        response = client.get("/country/Brazil")
        assert response.status_code == 404

        data = response.get_json()
        assert data["success"] is False
        assert "not found" in data["error"].lower()

    @patch("tools_server.RAPIDAPI_KEY", None)
    def test_missing_api_key(self):
        response = client.get("/country/France")
        assert response.status_code == 500

        data = response.get_json()
        assert data["success"] is False
        assert "RAPIDAPI_KEY" in data["error"]

    @patch("tools_server.RAPIDAPI_KEY", "fake_key")
    @patch("tools_server.httpx.get")
    def test_country_api_timeout(self, mock_get):
        mock_get.side_effect = httpx.TimeoutException("timeout")

        response = client.get("/country/France")
        assert response.status_code == 503

        data = response.get_json()
        assert data["success"] is False
        assert "timeout" in data["error"].lower()

    @patch("tools_server.RAPIDAPI_KEY", "fake_key")
    @patch("tools_server.httpx.get")
    def test_country_api_unauthorized(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        response = client.get("/country/France")
        assert response.status_code == 401

        data = response.get_json()
        assert data["success"] is False
        assert "status 401" in data["error"].lower()

    @patch("tools_server.RAPIDAPI_KEY", "fake_key")
    @patch("tools_server.httpx.get")
    def test_country_api_rate_limited(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Too Many Requests"
        mock_get.return_value = mock_response

        response = client.get("/country/France")
        assert response.status_code == 429

        data = response.get_json()
        assert data["success"] is False
        assert "status 429" in data["error"].lower()

    @patch("tools_server.RAPIDAPI_KEY", "fake_key")
    @patch("tools_server.httpx.get")
    def test_country_api_server_error(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Upstream server error"
        mock_get.return_value = mock_response

        response = client.get("/country/France")
        assert response.status_code == 500

        data = response.get_json()
        assert data["success"] is False
        assert "status 500" in data["error"].lower()

    @patch("tools_server.RAPIDAPI_KEY", "fake_key")
    @patch("tools_server.httpx.get")
    def test_country_special_characters(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "Côte d'Ivoire", "iso2": "CI"}
        ]
        mock_get.return_value = mock_response

        response = client.get("/country/C%C3%B4te%20d%27Ivoire")
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert data["data"]["name"] == "Côte d'Ivoire"

    @patch("tools_server.RAPIDAPI_KEY", "fake_key")
    @patch("tools_server.httpx.get")
    def test_country_unexpected_exception(self, mock_get):
        mock_get.side_effect = Exception("unexpected failure")

        response = client.get("/country/France")
        assert response.status_code == 500

        data = response.get_json()
        assert data["success"] is False
        assert "unexpected failure" in data["error"]


class TestGeneralEdgeCases:
    def test_unknown_route_returns_404(self):
        response = client.get("/does-not-exist")
        assert response.status_code == 404

    def test_main_endpoints_return_json_when_handled(self):
        response = client.get("/health")
        assert response.content_type.startswith("application/json")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
