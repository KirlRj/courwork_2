from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

import pytest
from requests.models import Response

from src.api_work import APIAdapter


@pytest.fixture
def adapter() -> APIAdapter:
    """Фикстура для создания экземпляра APIAdapter"""
    return APIAdapter()


def mock_response(json_data: Any, status: int = 200) -> MagicMock:
    """Создаём мок объекта requests.Response"""
    mock_resp: MagicMock = MagicMock(spec=Response)
    mock_resp.json.return_value = json_data
    mock_resp.status_code = status
    mock_resp.raise_for_status.return_value = None
    return mock_resp


@patch("requests.get")
def test_get_data_for_airplanes_success(mock_get: MagicMock, adapter: APIAdapter) -> None:
    """Проверка успешного получения данных о самолётах через API"""

    def side_effect(
        url: str, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None, timeout: int = 10
    ) -> MagicMock:
        if "nominatim" in url:
            return mock_response([{"boundingbox": ["1", "2", "3", "4"]}])
        else:
            return mock_response(
                {"states": [["abc123", "TEST123", "CountryX", 0, 0, 0, 0, 0, False, 0, 0, 0, 0, 10000]]}
            )

    mock_get.side_effect = side_effect

    data: Optional[Dict[str, Any]] = adapter.get_data_for_airplanes("Testland")
    assert data is not None
    assert "states" in data
    assert data["states"][0][0] == "abc123"
