import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List

from src.data_work import Airplane


class AbstractFileConnector(ABC):

    @abstractmethod
    def add_data(self, airplane: Airplane) -> None:
        """Добавление данных о самолете в файл"""
        pass

    @abstractmethod
    def get_data(self, **criteria: Any) -> List[Dict[str, Any]]:
        """Получение данных из файла по критериям"""
        pass

    @abstractmethod
    def delete_data(self, **criteria: Any) -> None:
        """Удаление данных из файла"""
        pass


class JSONFileConnector(AbstractFileConnector):

    def __init__(self, filename: str = "airplane_data.json") -> None:
        self.__filename = filename

    def __read_file(self) -> List[Dict[str, Any]]:
        if not os.path.exists(self.__filename):
            return []

        with open(self.__filename, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                return [dict(item) for item in data]
            except json.JSONDecodeError:
                return []

    def __write_file(self, data: List[Dict[str, Any]]) -> None:
        with open(self.__filename, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    def add_data(self, airplane: Airplane) -> None:

        data = self.__read_file()

        airplane_dict = {
            "icao24": airplane.icao24,
            "callsign": airplane.callsign,
            "on_ground": airplane.on_ground,
            "geo_altitude": airplane.geo_altitude,
            "origin_country": airplane.origin_country,
        }

        for plane in data:
            if plane["icao24"] == airplane_dict["icao24"]:
                return

        data.append(airplane_dict)

        self.__write_file(data)

    def get_data(self, **criteria: Any) -> List[Dict[str, Any]]:

        data = self.__read_file()

        if not criteria:
            return data

        result = []

        for plane in data:
            match = True

            for key, value in criteria.items():
                if plane.get(key) != value:
                    match = False
                    break

            if match:
                result.append(plane)

        return result

    def delete_data(self, **criteria: Any) -> None:

        data = self.__read_file()

        new_data = []

        for plane in data:
            match = True

            for key, value in criteria.items():
                if plane.get(key) != value:
                    match = False
                    break

            if not match:
                new_data.append(plane)

        self.__write_file(new_data)
