# Anastasia
# Spider that scraps boxofficemojo.com

from enum import Enum

import scrapy

from scrap_module.items import BoxOfficeMovie, Cast, BoxOfficeRegionIncome, BoxOfficeMovie, BoxOfficeRelease

NUMBER_OF_COLUMNS_IN_REGION = 4
NUMBER_OF_COLUMNS_IN_RELEASE = 6

column_selector = lambda num: f".//td[{num}]"


def get_table_information(response, field, additional=''):
    return response.xpath(
        f"//div[contains(@class, 'mojo-summary-table')]//span[contains(text(), '{field}')]/following-sibling::span{additional}/text()").get()


class BoxOfficeSpider(scrapy.Spider):
    name = "box_office"

    def __init__(self, start_urls=None, *args, **kwargs):
        super(BoxOfficeSpider, self).__init__(*args, **kwargs)
        self.start_urls = start_urls.split(",") if start_urls else []

    def parse(self, response):
        self.logger.info(f"Processing box office URL: {response.url}")

        opening_weekend = get_table_information(response, "Domestic Opening", additional="//span[@class='money']")
        box_office_link = response.url

        is_more_than_one_release = response.xpath(
            "//h3[text() = 'By Release' or text() = 'By Region']").get() is not None

        movie = BoxOfficeMovie(
            box_office_link=box_office_link,
            opening_weekend=opening_weekend,
            region_incomes=self._get_region_incomes(response, is_more_than_one_release),
            releases=self._get_releases(response, is_more_than_one_release),
        )

        cast_link = f"{box_office_link.split('?')[0]}credits"

        yield response.follow(cast_link, self._parse_cast, meta={"movie": movie})

    def _get_description_rows(self, response, number_of_columns):
        return response.xpath(
            f"//div[@class='a-section mojo-gutter']//table[@class='a-bordered a-horizontal-stripes a-size-base-plus' and count(.//th) = {number_of_columns}]//tr[count(.//th) = 0]")

    def _get_region_incomes(self, response, is_more_than_one_release):
        region_rows = self._get_description_rows(response, NUMBER_OF_COLUMNS_IN_REGION)

        region_incomes = []
        for region_row in region_rows:
            name = region_row.xpath(f"{column_selector(1)}//a/text()").get()
            release_amount = region_row.xpath(f"{column_selector(2)}/text()").get() if is_more_than_one_release else 1
            rank = region_row.xpath(f"{column_selector(4)}/text()").get() if is_more_than_one_release else None

            gross_idx = 3 if is_more_than_one_release else 4
            gross = region_row.xpath(f"{column_selector(gross_idx)}//span/text()").get()

            region_incomes.append(BoxOfficeRegionIncome(
                name=name,
                releases_amount=release_amount,
                rank=rank,
                gross=gross,
            ))

        return region_incomes

    def _get_releases(self, response, is_more_than_one_release):
        releases = []

        if is_more_than_one_release:
            release_rows = self._get_description_rows(response, NUMBER_OF_COLUMNS_IN_RELEASE)

            for release_row in release_rows:
                releases.append(BoxOfficeRelease(
                    date=release_row.xpath(f"{column_selector(2)}/text()"),
                    domestic_income=release_row.xpath(f"{column_selector(4)}//span/text()"),
                    international_income=release_row.xpath(f"{column_selector(5)}//span/text()"),
                    worldwide_income=release_row.xpath(f"{column_selector(6)}//span/text()")
                ))
        else:
            inboxes = response.xpath(
                "//div[contains(@class, 'mojo-performance-summary-table')]//span[@class='money']/text()").getall()

            releases.append(BoxOfficeRelease(
                date=get_table_information(response, "Earliest Release Date"),
                domestic_income=inboxes[0],
                international_income=inboxes[1],
                worldwide_income=inboxes[2]
            ))

        return releases

    def _parse_cast(self, response):
        movie = response.request.meta['movie']

        cast = []

        makers_rows = response.xpath("//table[@id='principalCrew']//tr[position() > 1]")
        cast_rows = makers_rows.xpath("//table[@id='principalCast']//tr[position() > 1]")

        name_selector = ".//td[1]/a/text()"

        for maker_row in makers_rows:
            cast.append(Cast(
                name=maker_row.xpath(name_selector).get(),
                position=maker_row.xpath(".//td[2]/text()").get(),
                role=None
            ))

        for cast_row in cast_rows:
            cast.append(Cast(
                name=cast_row.xpath(name_selector).get(),
                position="Actor",
                role=cast_row.xpath(".//td[2]//div[@class='a-expander-content a-expander-partial-collapse-content']/text()").get()
            ))

        movie['cast'] = cast

        yield movie
