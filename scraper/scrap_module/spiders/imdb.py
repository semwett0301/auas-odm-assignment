import time

import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def is_element_in_viewport(driver, element):
    location = element.location
    size = element.size

    window_height = driver.execute_script("return window.innerHeight")
    window_width = driver.execute_script("return window.innerWidth")

    return (0 <= location['x'] <= window_width and
            0 <= location['y'] <= window_height and
            location['y'] + size['height'] <= window_height)

def wait_for_element_to_disappear(driver, selector, timeout=30):
    element = driver.find_element(By.CSS_SELECTOR, selector)
    start_time = time.time()

    while time.time() - start_time < timeout:
        if not is_element_in_viewport(driver, element):
            return True

        time.sleep(0.5)
    return False

class ImdbClubSpider(scrapy.Spider):
    name = "imdb"

    _NEXT_BUTTON = 'button.ipc-see-more__button'
    _MOVIE_ELEM = '.ipc-metadata-list-summary-item'

    _PAGE_NUM = 5000

    def __init__(self, iterations=None, *args, **kwargs):
        super(ImdbClubSpider, self).__init__(*args, **kwargs)
        self.iterations = int(iterations) if iterations else None

    def start_requests(self):
        url = "https://www.imdb.com/search/title/?title_type=feature"
        yield SeleniumRequest(url=url, callback=self.parse)

    def parse(self, response):
        driver = response.request.meta["driver"]

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self._MOVIE_ELEM))
        )

        if self.iterations is None:
            iterations_element_text = driver.find_element(By.CSS_SELECTOR, ".fwjHEn").text
            self.iterations = int(''.join(iterations_element_text.split(" ")[-2:])) // self._PAGE_NUM + 1

        for i in range(0, self.iterations):
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self._NEXT_BUTTON))
            )
            driver.execute_script("arguments[0].click();", next_button)

            wait_for_element_to_disappear(driver, "button.ipc-btn")

        for product in driver.find_elements(By.CSS_SELECTOR, self._MOVIE_ELEM):
            url = product.find_element(By.CSS_SELECTOR, "a.ipc-title-link-wrapper").get_attribute("href")

            yield {'url': url}
