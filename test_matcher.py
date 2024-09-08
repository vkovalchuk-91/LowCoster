from datetime import datetime, timedelta
from itertools import product

flights1 = [{'from_city': 'city_1',
             'to_city': 'city_2',
             'from_time': datetime(2024, 12, 2),
             'to_time': datetime(2024, 12, 2),
             'total_price': 12},
            {'from_city': 'city_1',
             'to_city': 'city_4',
             'from_time': datetime(2024, 12, 2),
             'to_time': datetime(2024, 12, 2),
             'total_price': 7},
            {'from_city': 'city_3',
             'to_city': 'city_2',
             'from_time': datetime(2024, 12, 4),
             'to_time': datetime(2024, 12, 4),
             'total_price': 9}
            ]
flights2 = [{'from_city': 'city_2',
             'to_city': 'city_5',
             'from_time': datetime(2024, 12, 4),
             'to_time': datetime(2024, 12, 4),
             'total_price': 16},
            {'from_city': 'city_2',
             'to_city': 'city_6',
             'from_time': datetime(2024, 12, 5),
             'to_time': datetime(2024, 12, 5),
             'total_price': 14},
            {'from_city': 'city_4',
             'to_city': 'city_5',
             'from_time': datetime(2024, 12, 4),
             'to_time': datetime(2024, 12, 4),
             'total_price': 11}
            ]
flights3 = [{'from_city': 'city_6',
             'to_city': 'city_7',
             'from_time': datetime(2024, 12, 6),
             'to_time': datetime(2024, 12, 6),
             'total_price': 3},
            {'from_city': 'city_6',
             'to_city': 'city_8',
             'from_time': datetime(2024, 12, 8),
             'to_time': datetime(2024, 12, 8),
             'total_price': 8},
            {'from_city': 'city_5',
             'to_city': 'city_8',
             'from_time': datetime(2024, 12, 7),
             'to_time': datetime(2024, 12, 7),
             'total_price': 22}
            ]


def combine_flights(flights1, flights2, flights3):
    def is_valid_connection(flight1, flight2):
        # Перевіряємо чи точка прибуття з першого рейсу співпадає з точкою відбуття другого рейсу
        if flight1['to_city'] != flight2['from_city']:
            return False

        # Перевіряємо чи час між рейсами становить від 2 до 3 днів
        days_between = (flight2['from_time'] - flight1['to_time']).days
        return 2 <= days_between <= 3

    valid_routes = []

    # Створюємо всі можливі комбінації з трьох списків рейсів
    for flight1, flight2, flight3 in product(flights1, flights2, flights3):
        if is_valid_connection(flight1, flight2) and is_valid_connection(flight2, flight3):
            total_price = flight1['total_price'] + flight2['total_price'] + flight3['total_price']
            valid_routes.append({
                'route': [flight1, flight2, flight3],
                'total_price': total_price
            })

    # Сортуємо маршрути за спаданням загальної вартості
    sorted_routes = sorted(valid_routes, key=lambda x: x['total_price'])

    return sorted_routes


# Виклик функції
routes = combine_flights(flights1, flights2, flights3)

# Виводимо відсортовані маршрути
for route in routes:
    print("Маршрут:")
    for flight in route['route']:
        print(
            f"{flight['from_city']} -> {flight['to_city']} ({flight['from_time']} - {flight['to_time']}) Ціна: {flight['total_price']}")
    print(f"Загальна ціна: {route['total_price']}\n")
