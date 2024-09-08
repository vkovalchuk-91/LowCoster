import asyncio
import gzip
import io
import json
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver  # Використовуємо Selenium Wire для перехоплення запитів


def get_last_search_one_way_itineraries_query_request(driver_requests):
    default_request_url = 'https://api.skypicker.com/umbrella/v2/graphql?featureName=SearchOneWayItinerariesQuery'
    last_matching_request = None
    for driver_request in reversed(driver_requests):
        if default_request_url in driver_request.url:
            last_matching_request = driver_request
            break

    return last_matching_request


def close_warning_window_action(driver):
    close_button = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, '[data-test="ModalCloseButton"]'))
    )
    close_button.click()


def change_currency_action(driver, currency_code):
    currency_button = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, '[data-test="TopNav-RegionalSettingsButton"]'))
    )
    currency_button.click()
    currency_select = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, '[data-test="CurrencySelect"]'))
    )
    select = Select(currency_select)
    select.select_by_value(currency_code)
    submit_selected_currency_button = WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.CSS_SELECTOR, '[data-test="SubmitRegionalSettingsButton"]'))
    )
    submit_selected_currency_button.click()


def press_load_more_repeated_action(driver, loaded_pages_number):
    button_path = "//button[@type='button' and @role='button']//div[text()='Завантажити ще']/ancestor::button"
    button_inner_div_path = "//div[text()='Завантажити ще']"
    for i in range(loaded_pages_number):
        WebDriverWait(driver, 20).until(
            ec.visibility_of_element_located((By.XPATH, button_inner_div_path))
        )
        button = driver.find_element(By.XPATH, button_path)
        inner_html = button.get_attribute('outerHTML')
        print(inner_html)
        driver.execute_script("arguments[0].click();", button)


def parse_flights(request):
    with gzip.GzipFile(fileobj=io.BytesIO(request.response.body)) as gzip_file:
        response_text = gzip_file.read().decode('utf-8', errors='ignore')
        all_results_raw = []
        flights = []
        all_results_raw.extend(json.loads(response_text)['data']['onewayItineraries']['itineraries'])
        for result in all_results_raw:
            first_segment = result['sector']['sectorSegments'][0]['segment']
            flight_info = {'departure_station_code': first_segment['source']['station']['code'],
                           'departure_id': first_segment['source']['station']['id'],
                           'departure_city_name': first_segment['source']['station']['city']['name'],
                           'departure_city_id': first_segment['source']['station']['city']['id'],
                           'departure_name': first_segment['source']['station']['name'],
                           'departure_country_code': first_segment['source']['station']['country']['code'],
                           'departure_country_id': first_segment['source']['station']['country']['id'],
                           'arrival_station_code': first_segment['destination']['station']['code'],
                           'arrival_id': first_segment['destination']['station']['id'],
                           'arrival_city_name': first_segment['destination']['station']['city']['name'],
                           'arrival_city_id': first_segment['destination']['station']['city']['id'],
                           'arrival_name': first_segment['destination']['station']['name'],
                           'arrival_country_code': first_segment['destination']['station']['country']['code'],
                           'arrival_country_id': first_segment['destination']['station']['country']['id'],
                           'airline': first_segment['carrier']['name'],
                           'departure_local_time': datetime.fromisoformat(first_segment['source']['localTime']),
                           'departure_utc_time': datetime.fromisoformat(first_segment['source']['utcTime']),
                           'arrival_local_time': datetime.fromisoformat(first_segment['destination']['localTime']),
                           'arrival_utc_time': datetime.fromisoformat(first_segment['destination']['utcTime']),
                           'price': float(result['price']['amount']),
                           'price_eur': float(result['priceEur']['amount']),
                           'seats_left': result['lastAvailable']['seatsLeft']}

            if flight_info:
                flights.append(flight_info)
    return flights


def get_url(start_date, finish_date, departure_points, arrival_points):
    dates_string = get_dates_string(start_date, finish_date)
    departure_string = ','.join(departure_points)
    arrival_string = ','.join(arrival_points)
    return (f'https://www.kiwi.com/uk/search/results/{departure_string}/{arrival_string}/{dates_string}/no-return'
            f'?stopNumber=0%7Etrue&sortBy=price')


def get_dates_string(start_date, finish_date):
    # Перетворюємо дати на формат 'YYYY-MM-DD'
    date1_str = start_date.strftime('%Y-%m-%d')
    date2_str = finish_date.strftime('%Y-%m-%d')

    # Повертаємо строку у вигляді 'YYYY-MM-DD_YYYY-MM-DD'
    return f"{date1_str}_{date2_str}"


def get_flights(start_date, finish_date, departure_points, arrival_points, loaded_pages_number, currency_code):
    # Налаштовуємо Selenium Wire WebDriver
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    try:
        url = get_url(start_date, finish_date, departure_points, arrival_points)
        driver.get(url)

        close_warning_window_action(driver)
        change_currency_action(driver, currency_code)
        press_load_more_repeated_action(driver, loaded_pages_number)

        request = get_last_search_one_way_itineraries_query_request(driver.requests)
        parsed_flights = parse_flights(request)
        print(f"{parsed_flights[0]}")
        return parsed_flights

        # print(len(parsed_flights))
        # print(request.headers.get('kw-umbrella-token'))
        # print(json.loads(response_text))
    finally:
        # input("Натисніть Enter, щоб закрити браузер...")
        driver.quit()


async def main() -> None:
    ggg = get_flights(datetime.now(), datetime(2024, 12, 31),
                      ['польща'],
                      ['рим-італія', 'мілан-італія', 'ріміні-італія'],
                      5, 'usd')
    print(ggg)
    # await get_flights(datetime.now(), datetime(2024, 12, 31),
    #                   ['аеропорт-імені-фридерика-шопена-варшава-польща', 'краків-польща'],
    #                   ['рим-італія', 'мілан-італія'],
    #                   3, 'usd')


if __name__ == "__main__":
    asyncio.run(main())
