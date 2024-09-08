import asyncio

import requests

from db_operations import initialize_db, save_cities, save_airports, save_countries

headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'kw-skypicker-visitor-uniqid': '81eb3a3b-5cdb-4810-b708-ae16d5f7cb0f',
    'kw-umbrella-token': '29397ebd01ed0679b38fdd8ad78761bee4e30bc8786c2db98014a161056bd46a',
    'origin': 'https://www.kiwi.com',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.kiwi.com/',
    'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
}

ukrainian_alphabet = [
    'А', 'Б', 'В', 'Г', 'Ґ', 'Д', 'Е', 'Є', 'Ж', 'З', 'И', 'І', 'Ї', 'Й',
    'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч',
    'Ш', 'Щ', 'Ь', 'Ю', 'Я'
]


def get_places():
    countries = []
    unique_countries_ids = []
    cities = []
    unique_cities_ids = []
    airports = []
    unique_airports_ids = []
    for letter in ukrainian_alphabet:
        var_text = '{"search":{"term":"' + letter + '"},"filter":{"onlyTypes":["AIRPORT","COUNTRY","CITY"]},"options":{"locale":"uk","position":{"lat":50.458,"lng":30.5303}}}'
        params = {
            'featureName': 'UmbrellaPlacesQuery',
            'query': 'query UmbrellaPlacesQuery( $search: PlacesSearchInput $filter: PlacesFilterInput $options: PlacesOptionsInput ) { places(search: $search, filter: $filter, options: $options, first: 2000) { __typename ... on AppError { error: message } ... on PlaceConnection { edges { rank distance { __typename distance } isAmbiguous node { __typename __isPlace: __typename id legacyId name slug slugEn gps { lat lng } rank ... on City { code autonomousTerritory { legacyId id } subdivision { legacyId name id } country { legacyId name slugEn region { legacyId continent { legacyId id } id } id } airportsCount groundStationsCount } ... on Station { type code gps { lat lng } city { legacyId name slug autonomousTerritory { legacyId id } subdivision { legacyId name id } country { legacyId name region { legacyId continent { legacyId id } id } id } id } } ... on Region { continent { legacyId id } } ... on Country { code region { legacyId continent { legacyId id } id } } ... on AutonomousTerritory { country { legacyId name region { legacyId continent { legacyId id } id } id } } ... on Subdivision { country { legacyId name region { legacyId continent { legacyId id } id } id } } } } } } }',
            'variables': var_text,
        }
        response = requests.get('https://api.skypicker.com/umbrella/v2/graphql', params=params, headers=headers)

        all_results_raw = response.json()['data']['places']['edges']
        for result in all_results_raw:
            if result['node']['__typename'] == 'Country':
                place_info = {'typename': result['node']['__typename'],
                              'id': result['node']['id'],
                              'legacyId': result['node']['legacyId'],
                              'name': result['node']['name'],
                              'slug': result['node']['slug'],
                              'slugEn': result['node']['slugEn'],
                              'code': result['node']['code'],
                              'region_legacyId': result['node']['region']['legacyId'],
                              'region_id': result['node']['region']['id']}
                if place_info and result['node']['id'] not in unique_countries_ids:
                    unique_countries_ids.append(result['node']['id'])
                    countries.append(place_info)

            if result['node']['__typename'] == 'Station':
                place_info = {'typename': result['node']['__typename'],
                              'id': result['node']['id'],
                              'legacyId': result['node']['legacyId'],
                              'name': result['node']['name'],
                              'slug': result['node']['slug'],
                              'slugEn': result['node']['slugEn'],
                              'type': result['node']['type'],
                              'code': result['node']['code'],
                              'city_legacyId': result['node']['city']['legacyId'],
                              'city_id': result['node']['city']['id']}
                if place_info and result['node']['id'] not in unique_airports_ids:
                    unique_airports_ids.append(result['node']['id'])
                    airports.append(place_info)

            if result['node']['__typename'] == 'City':
                place_info = {'typename': result['node']['__typename'],
                              'id': result['node']['id'],
                              'legacyId': result['node']['legacyId'],
                              'name': result['node']['name'],
                              'slug': result['node']['slug'],
                              'slugEn': result['node']['slugEn'],
                              'code': result['node']['code'],
                              'country_legacyId': result['node']['country']['legacyId'],
                              'country_id': result['node']['country']['id']}

                if place_info and result['node']['id'] not in unique_cities_ids:
                    unique_cities_ids.append(result['node']['id'])
                    cities.append(place_info)
    return countries, cities, airports


async def main() -> None:
    countries, cities, airports = get_places()
    # print(response.text)
    print(len(countries))
    # print(f"{countries[0]}")
    print(len(cities))
    # print(f"{cities[0]}")
    print(len(airports))
    # for i in range(len(countries)):
    #     print(f"{airports[i]}")
    await initialize_db()
    await save_countries(countries)
    await save_cities(cities)
    await save_airports(airports)


if __name__ == "__main__":
    asyncio.run(main())
