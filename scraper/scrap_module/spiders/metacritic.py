from enum import Enum

import scrapy

from scrap_module.items import MetacriticMovie, MetacriticReview, Cast

class MetacriticSpider(scrapy.Spider):
    name = "metacritic"

    def __init__(self, start_urls=None, *args, **kwargs):
        super(MetacriticSpider, self).__init__(*args, **kwargs)
        self.start_urls = start_urls.split(",") if start_urls else []

    def parse(self, response):
        self.logger.info(f"Processing metacritic URL: {response.url}")

        title = response.xpath("//div[@data-testid='hero-title']//h1/text()").get()

        release_date = response.xpath(
            "//div[@data-testid='details-movie']//span[contains(@class, 'g-text-bold') and text()='Release Date']/following-sibling::span/text()").get()
        userscore = float(response.xpath(
            "//div[contains(@data-testid,'user-score-info')]//div[contains(@class,'c-siteReviewScore')]//span/text()").get())
        metascore = int(response.xpath(
            "//div[contains(@data-testid,'critic-score-info')]//div[contains(@class,'c-siteReviewScore')]//span/text()").get())
        movie_url = response.xpath("//a[contains(@href, 'http')]/@href").get()
        genres = [x.strip() for x in response.xpath(
            "//div[@data-testid='details-movie']//span[text()='Genres']/following-sibling::ul//span[@class='c-globalButton_label']/text()").getall()]
        mpaa = response.xpath(
            "//span[contains(@class, 'g-text-bold') and text()='Rating']/following-sibling::span/text()").get()
        duration = response.xpath(
            "//div[@data-testid='details-movie']//span[text()='Duration']/following-sibling::span/text()").get()

        meta_link = response.url

        movie = MetacriticMovie(
            title=title,
            release_date=release_date,
            meta_link=meta_link,
            movie_url=movie_url,
            metascore=metascore,
            userscore=userscore,
            genres=genres,
            mpaa=mpaa,
            duration=duration,
        )

        cast_url = f"{meta_link.split('?')[0]}credits"

        yield response.follow(cast_url, self._parse_cast, meta={
            "movie": movie
        })

    def _parse_cast(self, response):
        movie = response.request.meta['movie']

        cast_elements = response.xpath("//div[@class='c-productCredits g-outer-spacing-bottom-xlarge']")

        result_cast = []

        for cast_element in cast_elements:
            main_title = cast_element.xpath(".//h3/text()").get().strip().lower()

            rows = cast_element.xpath(".//dl//div[@class='u-grid-3column g-inner-spacing-medium']")

            for row in rows:
                name = row.xpath(".//a/text()").get().strip()

                role = row.xpath(".//dt/text()").get()
                role = role.split('/')[0].strip().lower() if role else None

                if main_title == 'cast':
                    cast = Cast(
                        name=name,
                        position=main_title,
                        role=role,
                    )
                else:
                    cast = Cast(
                        name=name,
                        position=role if role else main_title,
                        role=None
                    )

                result_cast.append(cast)

        movie['cast'] = result_cast

        yield movie