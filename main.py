import os
import sys
from typing import Any

from src.api_work import APIAdapter
from src.data_work import Airplane
from src.interface import build_airplanes_from_api, filter_by_registration_country, get_top_n_by_altitude
from src.work_with_file import JSONFileConnector

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":

    def run_console() -> Any:
        """
        Основная функция для взаимодействия с пользователем через консоль.

        Возможности:
        1. Ввести название страны для запроса информации о самолетах из opensky-network.org
        2. Получить топ N самолетов по высоте полета (N запрашивается у пользователя)
        3. Получить самолеты по стране их регистрации
        4. Сохранить самолеты в файл
        5. Просмотреть сохраненные самолеты
        """

        adapter = APIAdapter()
        storage = JSONFileConnector()

        # Для хранения последнего ответа API
        last_response = None
        last_country = None

        print("\n" + "-" * 60)
        print("СИСТЕМА ОТСЛЕЖИВАНИЯ САМОЛЕТОВ")
        print("-" * 60)
        print("Программа позволяет получать информацию о самолетах")
        print("в реальном времени через OpenSky Network API.\n")

        while True:
            print("\n" + "-" * 60)
            print("ГЛАВНОЕ МЕНЮ")
            print("-" * 60)
            print("  1. Получить самолёты по стране")
            print("  2. Получить топ N самолётов по высоте")
            print("  3. Получить самолёты по стране регистрации")
            print("  4. Сохранить самолёты в файл")
            print("  5. Просмотреть сохранённые самолёты")
            print("  0. Выход")
            print("-" * 60)

            choice = input("\n Введите номер действия: ").strip()

            if choice == "0":
                print("\n" + "-" * 60)
                print("Выход из программы...")
                print("-" * 60)
                break

            elif choice == "1":
                # 1. Получение самолетов по стране
                print("ПОИСК САМОЛЕТОВ ПО СТРАНЕ")

                while True:
                    country = input("Введите страну для запроса (например, France, Germany): ").strip()
                    if country:
                        break
                    print("Название страны не может быть пустым!")

                print(f"\n Запрашиваю данные для {country}...")
                response = adapter.get_data_for_airplanes(country)

                if isinstance(response, dict) and "error" in response:
                    print(f"\n Ошибка: {response['error']}")
                    continue

                last_response = response
                last_country = country

                planes = build_airplanes_from_api(response)

                print("Данные успешно получены!")
                print(f"\n  Всего найдено: {len(planes)} самолетов")

                if planes:
                    for i, plane in enumerate(planes, 1):
                        status = "На земле" if plane.on_ground else "В воздухе"
                        callsign = plane.callsign if plane.callsign else "без позывного"
                        print(f"\n  {i}. {status}")
                        print(f"     Позывной: {callsign}")
                        print(f"     Высота: {plane.geo_altitude:.0f} м")

            elif choice == "2":
                # 2. Топ N самолетов по высоте
                print("\n" + "-" * 30)
                print("          ТОП САМОЛЕТОВ ПО ВЫСОТЕ")
                print("-" * 30)

                if not last_response:
                    print("\nСначала выполните поиск по стране (пункт 1)!")
                    continue

                while True:
                    try:
                        n = int(input("Введите количество самолетов для топа (1-10): ").strip())
                        if 1 <= n <= 10:
                            break
                        print("Введите число от 1 до 10!")
                    except ValueError:
                        print("Введите целое число!")

                planes = build_airplanes_from_api(last_response)

                if not planes:
                    print("\nНет данных о самолетах!")
                    continue

                airborne_planes = [p for p in planes if not p.on_ground and p.geo_altitude > 100]

                if not airborne_planes:
                    print("\nНет самолетов в воздухе!")
                    continue

                top_planes = get_top_n_by_altitude(airborne_planes, min(n, len(airborne_planes)))

                print(f"\nТоп-{len(top_planes)} самолетов по высоте над {last_country}:")
                print("-" * 40)
                for i, plane in enumerate(top_planes, 1):
                    callsign = plane.callsign if plane.callsign else "без позывного"
                    print(f"  {i:2d}. {callsign:15s} - {plane.geo_altitude:6.0f} м")

            elif choice == "3":
                # 3. Фильтр по стране регистрации
                print("\n" + "-" * 30)
                print("ФИЛЬТР ПО СТРАНЕ РЕГИСТРАЦИИ")
                print("-" * 30)

                if not last_response:
                    print("\n Сначала выполните поиск по стране (пункт 1)!")
                    continue

                while True:
                    country = input(
                        "Введите страну регистрации для фильтрации (например, Russia, United States): "
                    ).strip()
                    if country:
                        break
                    print("Название страны не может быть пустым!")

                planes = build_airplanes_from_api(last_response)

                if not planes:
                    print("\nНет данных о самолетах!")
                    continue

                filtered = filter_by_registration_country(planes, country)

                if filtered:
                    print(f"\nНайдено {len(filtered)} самолетов, зарегистрированных в {country}:")
                    print("-" * 50)
                    for i, plane in enumerate(filtered[:10], 1):
                        callsign = plane.callsign if plane.callsign else "без позывного"
                        status = "на земле" if plane.on_ground else "в воздухе"
                        print(f"  {i:2d}. {callsign:15s} - {plane.geo_altitude:6.0f} м ({status})")

                    if len(filtered) > 10:
                        print(f"\n  ... и еще {len(filtered) - 10} самолетов")
                else:
                    print(f"\nСамолеты, зарегистрированные в {country}, не найдены")

            elif choice == "4":
                # 4. Сохранение в файл
                print("\n" + "-" * 30)
                print("СОХРАНЕНИЕ В ФАЙЛ")
                print("-" * 30)

                if not last_response:
                    print("\nСначала выполните поиск по стране (пункт 1)!")
                    continue

                planes = build_airplanes_from_api(last_response)

                if not planes:
                    print("\nНет данных для сохранения!")
                    continue

                saved_count = 0
                for plane in planes:
                    try:
                        storage.add_data(plane)
                        saved_count += 1
                    except Exception as e:
                        print(f"Ошибка при сохранении {plane.icao24}: {e}")

                print(f"\nСохранено {saved_count} в файл '{storage._JSONFileConnector__filename}'")

            elif choice == "5":
                # 5. Просмотр сохраненных самолетов
                print("\n" + "-" * 30)
                print("ПРОСМОТР СОХРАНЕННЫХ САМОЛЕТОВ")
                print("-" * 30)

                saved = storage.get_data()

                if not saved:
                    print("\nСохранённые самолёты отсутствуют.")
                    continue

                saved_planes = []
                for plane in saved:
                    try:
                        saved_planes.append(
                            Airplane(
                                icao24=plane["icao24"],
                                callsign=plane["callsign"],
                                on_ground=plane["on_ground"],
                                geo_altitude=plane["geo_altitude"],
                                origin_country=plane["origin_country"],
                            )
                        )
                    except Exception:
                        continue

                print(f"\nВсего сохранено: {len(saved_planes)} самолетов")

                if saved_planes:
                    print("\n  Последние сохраненные самолеты:")
                    print("-" * 50)
                    for i, plane in enumerate(saved_planes[-10:], 1):
                        callsign = plane.callsign if plane.callsign else "без позывного"
                        status = "на земле" if plane.on_ground else "в воздухе"
                        print(f"  {i:2d}. {callsign:15s} - {plane.geo_altitude:6.0f} м ({status})")

            else:
                print("\nНеверный ввод. Пожалуйста, выберите действие от 0 до 5.")

    print(run_console())
