from typing import Any, Dict, List, Optional

from src.data_work import Airplane


def get_top_n_by_altitude(planes: List[Airplane], n: int) -> List[Airplane]:
    """
    Возвращает топ N самолётов по высоте полёта.
    """
    return sorted(planes, key=lambda x: x.geo_altitude, reverse=True)[:n]


def filter_by_registration_country(planes: List[Airplane], country: str) -> List[Airplane]:
    """
    Фильтрует самолёты по стране регистрации.
    """
    return [plane for plane in planes if getattr(plane, "origin_country", "").lower() == country.lower()]


def build_airplanes_from_api(response: Optional[Dict[str, Any]]) -> List[Airplane]:
    """Преобразует JSON-ответ API в список объектов Airplane"""
    if not response or "states" not in response:
        return []

    airplanes: List[Airplane] = []
    states = response.get("states", [])

    for plane in states:
        if plane is None or len(plane) < 14:
            continue

        try:
            icao24: str = plane[0]
            callsign: Optional[str] = plane[1]  # Может быть None
            origin_country: Optional[str] = plane[2]  # Страна регистрации
            on_ground: bool = plane[8]

            geo_altitude: float = float(plane[7]) if plane[7] is not None else 0.0

            # Обрабатываем специальные значения высоты
            if geo_altitude < -900:
                geo_altitude = 0.0

            airplane = Airplane(
                icao24=icao24,
                callsign=callsign,
                on_ground=on_ground,
                geo_altitude=geo_altitude,
                origin_country=origin_country,
            )
            airplanes.append(airplane)

        except ValueError, TypeError, IndexError:
            continue

    return airplanes
