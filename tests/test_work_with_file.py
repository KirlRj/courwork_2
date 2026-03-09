import os
from typing import Any, Dict, Generator, List

import pytest

from src.data_work import Airplane
from src.work_with_file import JSONFileConnector


@pytest.fixture
def test_file() -> Generator[str, None, None]:
    """Фикстура для временного тестового файла"""
    filename = "test_airplanes.json"
    if os.path.exists(filename):
        os.remove(filename)
    yield filename
    if os.path.exists(filename):
        os.remove(filename)


@pytest.fixture
def connector() -> Generator[JSONFileConnector, None, None]:
    conn = JSONFileConnector("test_airplanes.json")
    yield conn
    import os

    if os.path.exists("test_airplanes.json"):
        os.remove("test_airplanes.json")


@pytest.fixture
def sample_airplanes() -> List[Airplane]:
    """Возвращает список тестовых объектов Airplane"""
    return [
        Airplane(icao24="ABC123", callsign="TEST1", on_ground=False, geo_altitude=10000, origin_country="USA"),
        Airplane(icao24="DEF456", callsign="TEST2", on_ground=True, geo_altitude=2000, origin_country="CAN"),
        Airplane(icao24="GHI789", callsign=None, on_ground=False, geo_altitude=5000, origin_country="USA"),
    ]


def test_add_and_get_data(connector: JSONFileConnector, sample_airplanes: List[Airplane]) -> None:
    """Проверка добавления данных и получения всех записей"""
    for plane in sample_airplanes:
        connector.add_data(plane)

    all_data: List[Dict[str, Any]] = connector.get_data()
    assert len(all_data) == 3

    first = all_data[0]
    assert first["icao24"] == "ABC123"
    assert first["callsign"] == "TEST1"
    assert first["on_ground"] is False
    assert first["geo_altitude"] == 10000
    assert first["origin_country"] == "USA"


def test_add_duplicate_does_not_repeat(connector: JSONFileConnector, sample_airplanes: List[Airplane]) -> None:
    """Проверка, что дубликаты по ICAO24 не добавляются"""
    connector.add_data(sample_airplanes[0])
    connector.add_data(sample_airplanes[0])  # повторно
    all_data: List[Dict[str, Any]] = connector.get_data()
    assert len(all_data) == 1  # должен остаться только один


def test_get_data_with_criteria(connector: JSONFileConnector, sample_airplanes: List[Airplane]) -> None:
    """Проверка получения данных с фильтром"""
    for plane in sample_airplanes:
        connector.add_data(plane)

    usa_planes: List[Dict[str, Any]] = connector.get_data(origin_country="USA")
    assert len(usa_planes) == 2

    on_ground_planes: List[Dict[str, Any]] = connector.get_data(on_ground=True)
    assert len(on_ground_planes) == 1
    assert on_ground_planes[0]["icao24"] == "DEF456"


def test_delete_data(connector: JSONFileConnector, sample_airplanes: List[Airplane]) -> None:
    """Проверка удаления данных по критериям"""
    for plane in sample_airplanes:
        connector.add_data(plane)

    connector.delete_data(origin_country="USA")
    remaining: List[Dict[str, Any]] = connector.get_data()
    assert len(remaining) == 1
    assert remaining[0]["icao24"] == "DEF456"

    # Удаление несуществующей записи не ломает файл
    connector.delete_data(origin_country="NONEXIST")
    remaining_after: List[Dict[str, Any]] = connector.get_data()
    assert len(remaining_after) == 1
