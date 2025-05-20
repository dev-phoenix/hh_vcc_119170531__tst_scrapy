# alcohelpercities.py
"""helper for AlcoSpider: Cities"""
import json
from abc import abstractmethod

import scrapy

from hhvc_001.spiders.params import (
    CITY_SET,
    CITY_DEF,
    CITY_UUID_DEF,
    CITIES_URL,
    START_URLS,
)
from hhvc_helper.hhvc_h_lib import HHVCSSHelper


class AlcoHelperCities(HHVCSSHelper):
    """Helper for cities from alkoteka.com"""

    cities = {}
    cities_page = 1
    city_choice = CITY_SET
    city_name = CITY_DEF
    city_uuid = CITY_UUID_DEF
    catalog_urls = START_URLS

    def get_cities(self):
        """
        collect cities uuid
        """
        url = CITIES_URL.format(page=self.cities_page)
        yield scrapy.Request(url=url, callback=self.parse_cities)

    def parse_cities(self, response):
        """
        collect cities uuid
        start parse
        """
        data = json.loads(response.text)
        for city in data["results"]:
            self.cities[city["name"]] = city["uuid"]

        if data["meta"]["has_more_pages"]:
            self.cities_page = self.cities_page + 1
            url = CITIES_URL.format(page=self.cities_page)
            yield scrapy.Request(url=url, callback=self.parse_cities)
        else:
            # print("sites: ", self.cities)
            if self.city_choice in self.cities:
                self.city_uuid = self.cities[self.city_choice]
                self.city_name = self.city_choice
            print(
                "\033[1;30;1;47mselected location:",
                self.city_name,
                self.city_uuid,
                "\033[0m",
            )

            # collect category products
            urls = self.catalog_urls
            print()
            print("urls", urls)
            print()
            for url in urls:
                url = self.url_to_rest(url, page=1)
                self.logp(f"catalog url: {url}")
                # print(scrapy.Request(
                # url=url, callback=self.parse_catalog).body)
                yield scrapy.Request(url=url, callback=self.parse_catalog)

    @abstractmethod
    def parse_catalog(self, response):
        """
        parse catalog pages
        """
