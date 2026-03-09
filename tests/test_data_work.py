import pytest

from src.data_work import Airplane


def test_airplane_init_valid() -> None:
    """Проверка корректной инициализации"""
    plane: Airplane = Airplane(
        icao24="abc123", callsign="TEST123", on_ground=False, geo_altitude=10000.0, origin_country="USA"
    )
    assert plane.icao24 == "ABC123"  # автоматически upper()
    assert plane.callsign == "TEST123"
    assert plane.on_ground is False
    assert plane.geo_altitude == 10000.0
    assert plane.origin_country == "USA"


def test_airplane_callsign_and_origin_country_none() -> None:
    """Проверка callsign и origin_country = None"""
    plane: Airplane = Airplane(
        icao24="def456", callsign=None, on_ground=True, geo_altitude=5000.0, origin_country=None
    )
    assert plane.callsign is None
    assert plane.origin_country is None


def test_airplane_icao24_validation() -> None:
    """Проверка валидации ICAO24"""
    with pytest.raises(ValueError):
        Airplane("123", "CALL", True, 1000.0, "USA")  # слишком короткий


def test_airplane_callsign_validation() -> None:
    """Проверка валидации callsign: должно падать на неверный тип"""
    with pytest.raises(ValueError):
        Airplane("abc123", 123, True, 1000.0, "USA")  # type: ignore


def test_airplane_on_ground_validation() -> None:
    """Проверка валидации on_ground"""
    with pytest.raises(ValueError):
        Airplane("abc123", "CALL", "yes", True, "USA")  # type: ignore


def test_airplane_altitude_validation() -> None:
    """Проверка валидации geo_altitude"""
    with pytest.raises(ValueError):
        Airplane("abc123", "CALL", True, -5000.0, "USA")  # ниже допустимого диапазона


def test_airplane_comparisons() -> None:
    """Проверка магических методов сравнения"""
    plane1: Airplane = Airplane("abc123", "A1", False, 1000.0, "USA")
    plane2: Airplane = Airplane("def456", "B2", True, 2000.0, "USA")
    plane3: Airplane = Airplane("abc123", "C3", False, 1000.0, "USA")

    # сравнение по высоте
    assert plane1 < plane2
    assert plane2 > plane1

    # сравнение на равенство по ICAO24
    assert plane1 == plane3
    assert plane1 != plane2


def test_airplane_repr() -> None:
    """Проверка __repr__"""
    plane: Airplane = Airplane("abc123", "TEST123", False, 10000.0, "USA")
    expected: str = "Airplane(ICAO24=ABC123, Callsign=TEST123, " "Country=USA, On_ground=False, Altitude=10000 м)"
    assert repr(plane) == expected

    # без callsign и origin_country
    plane2: Airplane = Airplane("def456", None, True, 5000.0, None)
    expected2: str = (
        "Airplane(ICAO24=DEF456, Callsign=без позывного, " "Country=неизвестна, On_ground=True, Altitude=5000 м)"
    )
    assert repr(plane2) == expected2


def test_airplane_to_dict() -> None:
    """Проверка метода to_dict"""
    plane: Airplane = Airplane("abc123", "TEST123", False, 10000.0, "USA")
    data: dict = plane.to_dict()
    assert data == {
        "icao24": "ABC123",
        "callsign": "TEST123",
        "on_ground": False,
        "geo_altitude": 10000.0,
        "origin_country": "USA",
    }
