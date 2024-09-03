import asyncio
import logging

from aiohttp import ClientSession, ClientConnectorError, InvalidURL
from bs4 import BeautifulSoup

HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
           'accept': '*/*'}
HOST = 'https://www.kiwi.com/'


class IncorrectURL(Exception):
    def __init__(self, message="Введений вами URL є некоректним"):
        self.message = message
        super().__init__(self.message)


async def parse_kiwi(url):
    response_text = await get_response_text(url)
    print(response_text)
    return extract_ads(response_text)


async def get_response_text(url):
    async with ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                logging.info(f'Response Error on {url}')
                return None


def extract_ads(response_text):
    response_flights = []

    if response_text:
        soup = BeautifulSoup(response_text, 'html.parser')
        # Знайти перший елемент з data-testid="listing-grid"
        response_flights_raw = soup.find_all('div', {'data-test': 'ResultCardWrapper'})

        if response_flights_raw:
            # Збираємо всі знайдені оголошення
            for flight_raw in response_flights_raw:
                flight_info = {}

                stations_raw = flight_raw.find_all('div', {'data-test': 'stationName'})
                flight_info['departure_station_code'] = stations_raw[0].response_text
                flight_info['arrival_station_code'] = stations_raw[1].response_text

                flight_info['airline'] = flight_raw.find('div', class_='orbit-carrier-logo').find('img')['title']

                times_raw = flight_raw.find_all('div', {'data-test': 'TripTimestamp'})
                flight_info['departure_time'] = times_raw[0].find('time')['datetime']
                flight_info['arrival_time'] = times_raw[1].find('time')['datetime']

                flight_info['price'] = flight_raw.find('div', {'data-test': 'ResultCardPrice'}).find('span').response_text

                if flight_info:
                    response_flights.append(flight_info)

    return response_flights


# def split_price(undivided_price):
#     # Знаходимо індекс останнього пробілу
#     last_space_index = undivided_price.rfind(' ')
#
#     # Якщо пробіл не знайдено, повертаємо весь текст як першу частину, а другу частину залишаємо порожньою
#     if last_space_index == -1:
#         return undivided_price, ''
#
#     # Розбиваємо текст на дві частини
#     price = undivided_price[:last_space_index]
#     currency = undivided_price[last_space_index + 1:]
#
#     return price, currency


async def test():
    url = 'https://www.kiwi.com/uk/search/results/%D0%B0%D0%B5%D1%80%D0%BE%D0%BF%D0%BE%D1%80%D1%82-%D1%96%D0%BC%D0%B5%D0%BD%D1%96-%D1%84%D1%80%D0%B8%D0%B4%D0%B5%D1%80%D0%B8%D0%BA%D0%B0-%D1%88%D0%BE%D0%BF%D0%B5%D0%BD%D0%B0-%D0%B2%D0%B0%D1%80%D1%88%D0%B0%D0%B2%D0%B0-%D0%BF%D0%BE%D0%BB%D1%8C%D1%89%D0%B0/%D1%80%D0%B8%D0%BC-%D1%96%D1%82%D0%B0%D0%BB%D1%96%D1%8F/2024-09-01_2024-09-10/no-return?stopNumber=0%7Etrue&sortBy=price'
    ads = await parse_kiwi(url)
    print(len(ads))
    for ad in ads:
        print(ad['ad_url'])

if __name__ == '__main__':
    asyncio.run(test())
