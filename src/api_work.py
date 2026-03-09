from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import requests


class AbstractAPIAdapter(ABC):

    @abstractmethod
    def _AbstractAPIAdapter__connect_to_api(
        self, url: str, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None
    ) -> Optional[requests.Response]:
        """
        Метод подключения к API
        """
        pass

    @abstractmethod
    def get_data_for_airplanes(self, country: str) -> Optional[Dict[str, Any]]:
        """
        Метод получения данных о самолетах в указанной стране
        """
        pass


class APIAdapter(AbstractAPIAdapter):
    """
    Получить данные с nominatim.openstreetmap.org и opensky-network.org
    """

    def __init__(self) -> None:
        self.__openstreetmap_url = "https://nominatim.openstreetmap.org/search"
        self.__opensky_url = "https://opensky-network.org/api/states/all"
        self.__aeroplanes = None

    def _AbstractAPIAdapter__connect_to_api(
        self, url: str, params: Dict[str, Any], headers: Optional[Dict[str, str]] = None
    ) -> Optional[requests.Response]:
        """Метод подключения к API. Наследуется с абстрактного метода"""
        try:
            # Запрос
            response = requests.get(url=url, params=params, headers=headers, timeout=10)

            # Статус
            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при подключении к API {url}: {e}")
            return None

    def get_data_for_airplanes(self, country: str) -> Optional[Dict[str, Any]]:
        """Метод получения данных о самолетах. На вход указывается одна страна. Наследуется с абстрактного метода"""

        # Получение данных через nominatim
        headers_nominatim = {
            "User-Agent": "test-app",
        }

        # Параметры для nominatim
        params_nominatim = {
            "q": country,
            "format": "json",
            "limit": 1,
        }

        # Подключение к API координат страны
        response = self._AbstractAPIAdapter__connect_to_api(
            self.__openstreetmap_url, params_nominatim, headers_nominatim
        )
        if not response:
            return {"error": f"Не удалось подключиться к nominatim для страны '{country}'"}

        data = response.json()

        if not data:
            return {"error": f"Страна '{country}' не найдена"}

        # Получение координат
        geo_coordinates = data[0].get("boundingbox")
        lamin = float(geo_coordinates[0])
        lamax = float(geo_coordinates[1])
        lomin = float(geo_coordinates[2])
        lomax = float(geo_coordinates[3])

        # Параметры для фильтрации самолетов
        params_opensky = {
            "lamin": lamin,
            "lamax": lamax,
            "lomin": lomin,
            "lomax": lomax,
        }

        # Подключение к API информации о самолетах
        response = self._AbstractAPIAdapter__connect_to_api(self.__opensky_url, params_opensky)

        if not response:
            return {"error": f"Не удалось подключиться к opensky для страны '{country}'"}

        self.__aeroplanes = response.json()

        return self.__aeroplanes

    @property
    def aeroplanes(self) -> None:
        """Метод для доступа к данным о самолетах"""
        return self.__aeroplanes
