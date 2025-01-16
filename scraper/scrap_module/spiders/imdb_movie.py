import re
import time

import scrapy
from scrap_module.items import ImdbMovieItem, ImdbReview, ImdbParentsGuide, ImdbOrganization
from scrapy_selenium import SeleniumRequest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def scroll_to_bottom(driver, wait_time=2):
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(wait_time)
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break

        last_height = new_height


class ImdbMovieSpider(scrapy.Spider):
    name = 'imdb_movie'

    def __init__(self, start_url=None, *args, **kwargs):
        super(ImdbMovieSpider, self).__init__(*args, **kwargs)
        self._start_url = start_url

    def start_requests(self):
        yield SeleniumRequest(url=self._start_url, callback=self.parse)

    def parse(self, response):
        self.logger.info(f"response: {response.url}")

        driver = response.request.meta["driver"]
        wait = WebDriverWait(driver, 5)

        scroll_to_bottom(driver, wait_time=1)

        title = wait.until(
            EC.presence_of_element_located((By.XPATH, '//span[@data-testid="hero__primary-text"]'))).text
        genres = self._get_genres(wait)
        release_date = self._get_release_date(wait)
        budget = self._get_budget(wait)

        result_movie = ImdbMovieItem(title=title, genres=genres, release_date=release_date, budget=budget)

        base_url = response.url.split('?')[0]

        # cast_page_link = self._get_cast_page(wait)
        parents_link = f"{base_url}parentalguide"
        reviews_link = f"{base_url}reviews"
        critic_link = f"{base_url}criticreviews"
        organization_link = f"{base_url}companycredits"

        yield SeleniumRequest(url=reviews_link, callback=self._parse_reviews,
                              meta={'movie': result_movie, 'critic_link': critic_link, 'parents_link': parents_link,
                                    'organization_link': organization_link})

    def _get_director(self, wait):
        try:
            director_element = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//a[contains(@href, "/name/") and contains(@href, "_dr_1")]')
                )
            )
            return director_element.text
        except TimeoutException:
            return "N/A"

    def _get_genres(self, wait):
        genre_elements = wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@class="ipc-chip-list__scroller"]/a')))
        return [genre.text for genre in genre_elements]

    def _get_release_date(self, wait):
        try:
            release_date = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                      '//a[contains(@href, "releaseinfo") and contains(@class, "ipc-metadata-list-item__list-content-item--link")]'))).text
            return release_date
        except TimeoutException:
            return "N/A"

    def _get_cast_page(self, wait):
        return wait.until(
            EC.presence_of_element_located((By.XPATH, '//a[@aria-label="See full cast and crew"]'))
        ).get_attribute('href')

    def _get_meta_link(self, wait):
        return wait.until(
            EC.presence_of_element_located((By.XPATH, '//a[@aria-label="See full cast and crew"]'))
        ).get_attribute('href')

    def _get_budget(self, wait):
        try:
            budget_element_text = wait.until(
                EC.presence_of_element_located((By.XPATH,
                                                '//li[@data-testid="title-boxoffice-budget"]//span[@class="ipc-metadata-list-item__list-content-item"]'))
            ).text
            match = re.search(r'\$([\d,]+)', budget_element_text)

            return int(match.group(1).replace(',', ''))
        except TimeoutException:
            return -1

    # def _parse_cast(self, response):
    #     movie = response.request.meta['movie']
    #     reviews_link = response.request.meta['reviews_link']
    #
    #     driver = response.request.meta["driver"]
    #     wait = WebDriverWait(driver, 10)
    #
    #     cast_elements = wait.until(
    #         EC.presence_of_all_elements_located((By.XPATH, '//table[contains(@class, "cast_list")]//tr')))
    #
    #     cast = []
    #     for row in cast_elements:
    #         try:
    #             actor_name = row.find_element(By.XPATH, './td[2]/a').text.strip()
    #             character_name = row.find_element(By.XPATH, './td[4]').text.strip()
    #             cast.append(ImdbCastMember(actor=actor_name, character=character_name))
    #         except NoSuchElementException:
    #             continue
    #
    #     movie['cast'] = cast
    #
    #     yield SeleniumRequest(
    #         url=reviews_link, callback=self._parse_reviews,
    #         meta={'movie': movie, 'critic_link': response.meta['critic_link']},
    #     )

    def _get_element_text_or_default(self, element, xpath, default_value=None):
        try:
            return element.find_element(By.XPATH, xpath).text
        except:
            return default_value

    def _parse_reviews(self, response):
        movie = response.request.meta['movie']

        driver = response.request.meta["driver"]
        critic_link = response.request.meta['critic_link']

        wait = WebDriverWait(driver, 10)

        all_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button//span[text()='All']")))
        driver.execute_script("arguments[0].click();", all_button)

        scroll_to_bottom(driver)

        result_reviews = []
        for review in wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//article[contains(@class, "user-review-item")]'))
        ):
            score = self._get_element_text_or_default(review, './/span[@class="ipc-rating-star--rating"]')
            review_body = self._get_element_text_or_default(review, './/div[@class="ipc-html-content-inner-div"]')
            date = self._get_element_text_or_default(review, './/li[@class="ipc-inline-list__item review-date"]')
            author = self._get_element_text_or_default(review, './/a[@data-testid="author-link"]')

            result_reviews.append(ImdbReview(author=author, date=date, body=review_body, score=score))

        movie['reviews'] = result_reviews

        yield SeleniumRequest(
            url=critic_link, callback=self._parse_critic,
            meta=response.request.meta,
        )

    def _parse_critic(self, response):
        movie = response.request.meta['movie']
        parents_link = response.request.meta['parents_link']

        driver = response.request.meta["driver"]
        wait = WebDriverWait(driver, 10)

        meta_link = wait.until(
            EC.presence_of_element_located((By.XPATH, '//a[text() = "Metacritic.com"]'))
        ).get_attribute('href')

        movie['meta_link'] = meta_link

        yield SeleniumRequest(
            url=parents_link, callback=self._parse_parents,
            meta=response.request.meta,
        )

    def _parse_parents(self, response):
        movie = response.request.meta['movie']
        organization_link = response.request.meta['organization_link']

        driver = response.request.meta["driver"]
        wait = WebDriverWait(driver, 10)

        try:
            parents_parameters = [x.text for x in wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//li[@data-testid="rating-item"]//div[@class="ipc-html-content-inner-div"]'))
            )]

            movie['parents_guide'] = ImdbParentsGuide(
                sex_and_nudity=parents_parameters[0],
                violance=parents_parameters[1],
                frightening=parents_parameters[2],
                alcho=parents_parameters[3],
                profanity=parents_parameters[4],
            )
        finally:
            yield SeleniumRequest(
                url=organization_link, callback=self._parse_organization,
                meta=response.request.meta,
            )

    def _parse_organization(self, response):
        movie = response.request.meta['movie']

        driver = response.request.meta["driver"]
        wait = WebDriverWait(driver, 10)

        try:
            companies_result = []

            companies_sections = wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, '//section[@class="ipc-page-section ipc-page-section--base"]'))
            )

            for section in companies_sections:
                company_type = section.find_element(By.XPATH, './/a//h3//span').text

                for company in section.find_elements(By.XPATH, './/li//a[contains(@class, "ipc-metadata-list-item__label")]'):
                    companies_result.append(ImdbOrganization(type=company_type, name=company.text))

            movie['companies'] = companies_result
        finally:
            yield movie
