from typing import Any, Dict, List, Optional

from src.data_work import Airplane
from src.interface import build_airplanes_from_api, filter_by_registration_country, get_top_n_by_altitude


def test_get_top_n_by_altitude() -> None:
    """Проверка функции get_top_n_by_altitude"""
    planes: List[Airplane] = [
        Airplane("a12345", "PL1", False, 1000.0, "USA"),
        Airplane("b12345", "PL2", True, 5000.0, "Russia"),
        Airplane("c12345", "PL3", False, 2000.0, "USA"),
    ]

    top_planes: List[Airplane] = get_top_n_by_altitude(planes, 2)
    assert len(top_planes) == 2
    assert top_planes[0].geo_altitude == 5000.0
    assert top_planes[1].geo_altitude == 2000.0


def test_get_top_n_by_altitude_n_larger_than_list() -> None:
    """Если N больше числа самолётов, вернуть всех"""
    planes: List[Airplane] = [
        Airplane("a12345", "PL1", False, 1000.0, "USA"),
        Airplane("b12345", "PL2", True, 5000.0, "Russia"),
    ]
    top_planes: List[Airplane] = get_top_n_by_altitude(planes, 5)
    assert len(top_planes) == 2


def test_filter_by_registration_country() -> None:
    """Проверка фильтрации по стране регистрации"""
    planes: List[Airplane] = [
        Airplane("a12345", "PL1", False, 1000.0, "USA"),
        Airplane("b12345", "PL2", True, 5000.0, "Russia"),
        Airplane("c12345", "PL3", False, 2000.0, "USA"),
    ]

    filtered: List[Airplane] = filter_by_registration_country(planes, "USA")
    assert len(filtered) == 2
    for plane in filtered:
        assert plane.origin_country == "USA"

    filtered_lower: List[Airplane] = filter_by_registration_country(planes, "russia")
    assert len(filtered_lower) == 1
    assert filtered_lower[0].origin_country == "Russia"


def test_filter_by_registration_country_no_matches() -> None:
    """Если нет совпадений, вернуть пустой список"""
    planes: List[Airplane] = [
        Airplane("a12345", "PL1", False, 1000.0, "USA"),
        Airplane("b12345", "PL2", True, 5000.0, "Russia"),
    ]

    filtered: List[Airplane] = filter_by_registration_country(planes, "China")
    assert filtered == []


def test_build_airplanes_from_api_valid() -> None:
    """Проверка корректного преобразования API-ответа в список Airplane"""
    response: Dict[str, Any] = {
        "states": [
            ["abc123", "TEST123", "CountryX", 0, 0, 0, 0, 12000.0, False, 0, 0, 0, 0, 0],
            ["def456", "CALL456", "CountryY", 0, 0, 0, 0, None, True, 0, 0, 0, 0, 0],
            ["ghi789", None, "CountryZ", 0, 0, 0, 0, -1000.0, False, 0, 0, 0, 0, 0],
        ]
    }

    airplanes: List[Airplane] = build_airplanes_from_api(response)

    assert len(airplanes) == 3

    assert airplanes[0].icao24 == "ABC123"
    assert airplanes[0].callsign == "TEST123"
    assert airplanes[0].on_ground is False
    assert airplanes[0].geo_altitude == 12000.0
    assert airplanes[0].origin_country == "CountryX"

    assert airplanes[1].geo_altitude == 0.0

    assert airplanes[2].callsign is None
    assert airplanes[2].geo_altitude == 0.0


def test_build_airplanes_from_api_empty() -> None:
    """Проверка, что пустой ответ возвращает пустой список"""
    empty_response: Optional[Dict[str, Any]] = None
    airplanes: List[Airplane] = build_airplanes_from_api(empty_response)
    assert airplanes == []

    empty_response2: Dict[str, Any] = {}
    airplanes2: List[Airplane] = build_airplanes_from_api(empty_response2)
    assert airplanes2 == []


def test_build_airplanes_from_api_invalid_entries() -> None:
    """Проверка, что некорректные записи игнорируются"""
    response: Dict[str, Any] = {
        "states": [
            None,
            ["short"],  # меньше 14 элементов
            ["valid1", "CS1", "USA", 0, 0, 0, 0, 1000.0, False, 0, 0, 0, 0, 0],
        ]
    }
    airplanes: List[Airplane] = build_airplanes_from_api(response)
    assert len(airplanes) == 1
    assert airplanes[0].icao24 == "VALID1"
