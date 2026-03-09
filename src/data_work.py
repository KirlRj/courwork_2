from typing import Optional


class Airplane:
    """Класс для работы с данными о самолетах"""

    __slots__ = ("icao24", "callsign", "on_ground", "geo_altitude", "origin_country")

    def __init__(
        self, icao24: str, callsign: Optional[str], on_ground: bool, geo_altitude: float, origin_country: Optional[str]
    ) -> None:
        self.icao24 = self.__validate_icao24(icao24)
        self.callsign = self.__validate_callsign(callsign)
        self.on_ground = self.__validate_on_ground(on_ground)
        self.geo_altitude = self.__validate_altitude(geo_altitude)
        self.origin_country = self.__validate_origin_country(origin_country)

    def __validate_icao24(self, value: str) -> str:
        """Валидация ICAO24 кода"""
        if not isinstance(value, str):
            raise ValueError(f"ICAO24 должен быть строкой, получен {type(value).__name__}")
        if len(value) != 6:
            raise ValueError(f"ICAO24 должен содержать 6 символов, получено {len(value)}")
        return value.upper()

    def __validate_callsign(self, value: Optional[str]) -> Optional[str]:
        """Валидация позывного (может быть None)"""
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError(f"Позывной должен быть строкой или None, получен {type(value).__name__}")
        stripped = value.strip()
        return stripped if stripped else None

    def __validate_on_ground(self, value: bool) -> bool:
        """Валидация статуса на земле"""
        if not isinstance(value, bool):
            raise ValueError(f"on_ground должен быть True или False, получен {type(value).__name__}")
        return value

    def __validate_altitude(self, value: float) -> float:
        """Валидация высоты"""
        if not isinstance(value, (int, float)):
            raise ValueError(f"Высота должна быть числом, получен {type(value).__name__}")
        if value < -1000 or value > 50000:
            raise ValueError(f"Высота должна быть в диапазоне [-1000, 50000] метров, получена {value}")
        return float(value)

    def __validate_origin_country(self, value: Optional[str]) -> Optional[str]:
        """Валидация страны регистрации (может быть None)"""
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError(f"Страна регистрации должна быть строкой или None, получен {type(value).__name__}")
        stripped = value.strip()
        return stripped if stripped else None

    def __lt__(self, other: "Airplane") -> bool:
        """Сравнение по высоте (меньше)"""
        if not isinstance(other, Airplane):
            return NotImplemented
        return self.geo_altitude < other.geo_altitude

    def __gt__(self, other: "Airplane") -> bool:
        """Сравнение по высоте (больше)"""
        if not isinstance(other, Airplane):
            return NotImplemented
        return self.geo_altitude > other.geo_altitude

    def __eq__(self, other: object) -> bool:
        """Сравнение на равенство по ICAO24"""
        if not isinstance(other, Airplane):
            return NotImplemented
        return self.icao24 == other.icao24

    def __repr__(self) -> str:
        """Строковое представление"""
        callsign_str = self.callsign if self.callsign else "без позывного"
        country_str = self.origin_country if self.origin_country else "неизвестна"
        return (
            f"Airplane(ICAO24={self.icao24}, Callsign={callsign_str}, "
            f"Country={country_str}, On_ground={self.on_ground}, "
            f"Altitude={self.geo_altitude:.0f} м)"
        )

    def to_dict(self) -> dict:
        """Преобразование в словарь для сохранения"""
        return {
            "icao24": self.icao24,
            "callsign": self.callsign,
            "on_ground": self.on_ground,
            "geo_altitude": self.geo_altitude,
            "origin_country": self.origin_country,
        }
