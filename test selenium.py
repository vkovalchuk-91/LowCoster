import gzip
import io
import json


from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC, expected_conditions
from seleniumwire import webdriver  # Використовуємо Selenium Wire для перехоплення запитів

# Налаштовуємо Selenium Wire WebDriver
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)

def get_last_request(driver_requests):
    default_request_url = 'https://api.skypicker.com/umbrella/v2/graphql?featureName=SearchOneWayItinerariesQuery'
    last_matching_request = None
    for driver_request in reversed(driver_requests):
        if default_request_url in driver_request.url:
            last_matching_request = driver_request
            break

    return last_matching_request


try:
    # Відкриваємо потрібний URL
    url = 'https://www.kiwi.com/uk/search/results/%D0%B0%D0%B5%D1%80%D0%BE%D0%BF%D0%BE%D1%80%D1%82-%D1%96%D0%BC%D0%B5%D0%BD%D1%96-%D1%84%D1%80%D0%B8%D0%B4%D0%B5%D1%80%D0%B8%D0%BA%D0%B0-%D1%88%D0%BE%D0%BF%D0%B5%D0%BD%D0%B0-%D0%B2%D0%B0%D1%80%D1%88%D0%B0%D0%B2%D0%B0-%D0%BF%D0%BE%D0%BB%D1%8C%D1%89%D0%B0/%D1%80%D0%B8%D0%BC-%D1%96%D1%82%D0%B0%D0%BB%D1%96%D1%8F/2024-09-01_2024-12-31/no-return?stopNumber=0%7Etrue&sortBy=price'
    driver.get(url)

    # Очікуємо появи елемента div[data-test='ResultCardWrapper']
    button_path = "//button[@type='button' and @role='button']//div[text()='Завантажити ще']/ancestor::button"
    button_inner_div_path = "//div[text()='Завантажити ще']"

    close_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="ModalCloseButton"]'))
    )
    close_button.click()

    currency_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="TopNav-RegionalSettingsButton"]'))
    )
    currency_button.click()

    currency_select = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="CurrencySelect"]'))
    )
    select = Select(currency_select)
    select.select_by_value("usd")

    submit_selected_currency_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="SubmitRegionalSettingsButton"]'))
    )
    submit_selected_currency_button.click()

    for i in range(3):
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, button_inner_div_path))
        )
        button = driver.find_element(By.XPATH, button_path)
        inner_html = button.get_attribute('outerHTML')
        print(inner_html)
        driver.execute_script("arguments[0].click();", button)

    last_request = get_last_request(driver.requests)
    with gzip.GzipFile(fileobj=io.BytesIO(last_request.response.body)) as gzip_file:
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
                           'departure_local_time': first_segment['source']['localTime'],
                           'departure_utc_time': first_segment['source']['utcTime'],
                           'arrival_local_time': first_segment['destination']['localTime'],
                           'arrival_utc_time': first_segment['destination']['utcTime'],
                           'price': result['price']['amount'],
                           'price_eur': result['priceEur']['amount'],
                           'seats_left': result['lastAvailable']['seatsLeft']}

            if flight_info:
                flights.append(flight_info)
    print(len(flights))
    print(f"{flights[0]}")
    print(last_request.headers.get('kw-umbrella-token'))

    # # Всі запити після завантаження сторінки
    # for request in driver.requests:
    #     request_text = 'https://api.skypicker.com/umbrella/v2/graphql?featureName=SearchOneWayItinerariesQuery'
    #     if request.response and request_text in request.url:
    #         with gzip.GzipFile(fileobj=io.BytesIO(request.response.body)) as gzip_file:
    #             response_text = gzip_file.read().decode('utf-8', errors='ignore')
    #             all_results_raw = []
    #             flights = []
    #             all_results_raw.extend(json.loads(response_text)['data']['onewayItineraries']['itineraries'])
    #             for result in all_results_raw:
    #                 first_segment = result['sector']['sectorSegments'][0]['segment']
    #                 flight_info = {'departure_station_code': first_segment['source']['station']['code'],
    #                                'departure_id': first_segment['source']['station']['id'],
    #                                'departure_city_name': first_segment['source']['station']['city']['name'],
    #                                'departure_city_id': first_segment['source']['station']['city']['id'],
    #                                'departure_name': first_segment['source']['station']['name'],
    #                                'departure_country_code': first_segment['source']['station']['country']['code'],
    #                                'departure_country_id': first_segment['source']['station']['country']['id'],
    #                                'arrival_station_code': first_segment['destination']['station']['code'],
    #                                'arrival_id': first_segment['destination']['station']['id'],
    #                                'arrival_city_name': first_segment['destination']['station']['city']['name'],
    #                                'arrival_city_id': first_segment['destination']['station']['city']['id'],
    #                                'arrival_name': first_segment['destination']['station']['name'],
    #                                'arrival_country_code': first_segment['destination']['station']['country']['code'],
    #                                'arrival_country_id': first_segment['destination']['station']['country']['id'],
    #                                'airline': first_segment['carrier']['name'],
    #                                'departure_local_time': first_segment['source']['localTime'],
    #                                'departure_utc_time': first_segment['source']['utcTime'],
    #                                'arrival_local_time': first_segment['destination']['localTime'],
    #                                'arrival_utc_time': first_segment['destination']['utcTime'],
    #                                'price': result['price']['amount'],
    #                                'price_eur': result['priceEur']['amount'],
    #                                'seats_left': result['lastAvailable']['seatsLeft']}
    #
    #                 if flight_info:
    #                     flights.append(flight_info)
    #
    #             # print(response_text)
    #             print(len(flights))
    #             print(f"{flights[0]}")
    #             print(request.headers.get('kw-umbrella-token'))
    #         # print(
    #         #     f"Запит: {request.url}\n"
    #         #     f"Метод: {request.method}\n"
    #         #     f"Статус-код: {request.response.status_code}\n"
    #         #     f"Відповідь: {response_text}\n"
    #         # )
finally:
    input("Натисніть Enter, щоб закрити браузер...")
    driver.quit()
