"""
quotes_spider.py
tz: https://docs.google.com/document/d/\
19mLRcZKbezZl9SCv709UcpcssFJycez6/edit?tab=t.0
"""

from pathlib import Path
from copy import deepcopy as dp
import json
import urllib.parse as up
import time
import random

# import re
import logging

# from bs4 import BeautifulSoup as bs
import scrapy

# from scrapy.exporters import JsonItemExporter

from hhvc_helper.hhvc_h_lib import HHVCSSHelper
from hhvc_helper.models import OUT_TPL
from hhvc_001.spiders.params import (
    START_URLS,
)
from .alcohelpercities import AlcoHelperCities
from .alcohelperproxy import AlcoHelperProxy


log = logging.getLogger("scrapy.proxies")


class AlcoSpider(scrapy.Spider, AlcoHelperCities, AlcoHelperProxy):
    """Spider for alkoteka.com"""

    name = "alco"

    custom_settings = {
        "DOWNLOAD_DELAY": 0.25,  # 250 ms of delay
    }
    debug = (False,)

    product_urls = {}
    catalog_parsed_count = 0
    catalog_urls = START_URLS
    catalogs_file = False

    max_result = 10

    # proxy
    # https://proxy5.net/ru/free-proxy
    proxy_list = []

    scenario = "get proxy"

    def __init__(
        self,
        *args,
        scenario=None,
        proxy_from=None,
        proxy_count=None,
        proxy_on=None,
        **kwargs,
    ):
        """
        initialization
        """
        super(AlcoSpider, self).__init__(*args, **kwargs)
        # super(*args, **kwargs)

        city=kwargs.get("city", None)
        catalogs_file=kwargs.get("catalogs_file", None)
        product_count=kwargs.get("product_count", None)
        debug=kwargs.get("debug", None)

        if scenario == "proxy":
            self.scenario = "get proxy"
        else:
            self.scenario = "get alco"
        if proxy_from:
            self.proxy_from = proxy_from
            ext = self.proxy_from.split(".")[-1]
            self.proxy_scenario = ext
        if proxy_count:
            try:
                proxy_count = int(proxy_count)
            except Exception as e:
                err = e
                err = err
            else:
                self.get_proxy_count = str(proxy_count)
        if proxy_on in ["on", "off"] and proxy_on == "on":
            self.proxy_on = True

        if city:
            self.city_choice = city
        if catalogs_file:
            self.catalogs_file = catalogs_file
        self.collect_catalogs()
        if product_count:
            self.max_result = int(product_count)
        if debug:
            self.debug = True

        self.logp(f"proxy scenario: {self.proxy_scenario}")
        self.attrdump()

    def collect_catalogs(self):
        """collect catalog urls from file"""
        self.logp("catalog_urls", self.catalog_urls)
        if not self.catalogs_file:
            return
        self.catalog_urls = []
        with open(self.catalogs_file, "r", encoding="utf-8") as file:
            for row in file:
                if row:
                    self.catalog_urls.append(row)

    async def start(self):
        """
        version: latest (v2.13)
        """
        self.start_requests()

    def start_requests(self):
        """
        version: v2.11
        """
        self.attrdump()
        # urls = [
        #     "https://quotes.toscrape.com/page/1/",
        #     "https://quotes.toscrape.com/page/2/",
        #     # "https://quotes.toscrape.com/page/1/",
        #     # "https://quotes.toscrape.com/page/2/",
        # ]
        # url = CITIES_URL.format(page=self.cities_page)
        # yield scrapy.Request(url=url, callback=self.parse)

        self.load_proxy(self.proxy_from)
        # return

        # self.scenario = "get alco"
        # self.scenario = "get proxy"
        self.logp("scenario:", self.scenario.strip())

        if self.scenario.strip() == "get proxy":
            return self.get_proxy()

        if self.scenario.strip() == "get alco":
            return self.get_cities()
        return None

    def load_proxy(self, file_name: str = "proxy.json") -> None:
        """Load proxies from file"""

        # json_proxy = Path(file_name).read()
        with open(file_name, "r", encoding="utf-8") as file:
            if self.proxy_scenario == "txt":
                data = []
                for row in file:
                    row = row.strip()
                    if row and row[0] != "#":
                        data.append(row)
            else:
                data = json.load(file)
            for p in data:
                if self.is_dict(p):
                    p = p["proxy"]
                self.proxy_list.append(p)

    def parse(self, response, **kwargs):
        """
        abstract method
        """
        b = False
        if b:
            print("parse")
            print(response)
        yield "item"

    def parse_catalog(self, response):
        """
        parse catalog pages
        """
        self.logp("parse catalog pages")
        # print(f"status: {response.status}")
        # print("response: ", dir(response))

        url = response.url
        self.logp("url:", url, fg=31, bg=46)

        data = response.json()
        # print("data: ", data)

        # self.product_urls.extend(\
        # res["product_url"] for res in data["results"])
        for res in data["results"]:
            name = res["product_url"].split("/")[-1]
            self.product_urls[name] = {"url": res["product_url"]}
        pcou = len(self.product_urls)
        self.log(f"\033[1;30;1;47mproducts count: {pcou}\033[0m")

        if data["meta"]["has_more_pages"]:
            url = self.url_page_increment(url)
            self.logp(f"next catalog url: {url}")
            self.log("\033[1;30;1;47mcatalog url:" + url + "\033[0m")
            # print(scrapy.Request(
            # url=url, callback=self.parse_catalog).body)
            # yield scrapy.Request(url=url, callback=self.parse_catalog)

            # get catalgo
            request = scrapy.Request(url=url, callback=self.parse_catalog)
            # request.meta['proxy'] = "host:port"
            yield request
        else:
            self.catalog_parsed_count = self.catalog_parsed_count + 1
            c1 = self.catalog_parsed_count
            c2 = len(self.catalog_urls)
            self.logp(f"got catalog item: {c1} of {c2}")
            if self.catalog_parsed_count == len(self.catalog_urls):
                # collect products data
                self.logp("Start collecting products data", fg=31)
                urls = self.product_urls
                max_result = self.max_result
                self.logp("max_result", type(self.max_result))
                for name, url in urls.items():
                    if self.max_result and max_result == 0:
                        self.logp(f"reached limit of items: {self.max_result}")
                        break
                    c3 = self.max_result - max_result
                    self.logp(f"reached items: {c3}")
                    max_result -= 1
                    url = url["url"]
                    name = url.split("/")[-1]
                    url = self.url_to_rest(url)
                    self.logp(f"product url: {url}")
                    # print(scrapy.Request(
                    # url=url, callback=self.parse_catalog).body)

                    # get page
                    req = scrapy.Request(url=url, callback=self.parse_page)
                    if self.proxy_on and self.proxy_list:
                        proxy = random.choice(self.proxy_list)
                        if self.is_dict(proxy):
                            proxy = proxy["proxy"]
                        # proxy = f'https://{proxy}'
                        proxy = f"{proxy}"
                        print(proxy)
                        req.meta["proxy"] = proxy
                        # path = up.urlparse(response.url).path
                        # name = path.split("/")[-1]
                        self.product_urls[name]["proxy"] = proxy
                    yield req
                self.logp(f"to parse cou: {self.max_result}")

        # page = response.url.split("/")[-2]

        # filename = f"quotes-{page}.html"
        # Path(filename).write_bytes(response.body)
        # self.log(f"Saved file {filename}")

        # item = {
        #     "title": response.css("title::text").get(),
        #     "description": response.css(
        #         'meta[name="description"]::attr(content)'
        #     ).get(),
        # }
        # item = dp(OUT_TPL)
        # item["url"] = response.url
        # item["title"] = response.css("title::text").get()
        # yield item

        # next_page = response.css("li.next a::attr(href)").get()
        # urls = response.css("li.next a::attr(href)").get()
        # for url in urls:
        #     print(f'item url: {url}')
        #     yield scrapy.Request(url=url, callback=self.parse_page)

    product_get_marker = 3

    def parse_page(self, response):
        """parse item pages"""
        print(f"status: {response.status}")
        path = up.urlparse(response.url).path
        name = path.split("/")[-1]
        url = self.product_urls[name]["url"]
        proxy = ""
        if "proxy" in self.product_urls[name]:
            proxy = self.product_urls[name]["proxy"]
        self.logp("url:", url, fg=31, bg=46)
        self.logp("url:", url, fg=31, bg=46)
        data = response.json()

        if self.product_get_marker > 0:
            # page = response.url.split("/")[-2]
            filename = f"quotes-{name}.json"
            Path(filename).write_bytes(response.body)
            self.log(f"Saved file {filename}")

            self.product_get_marker = self.product_get_marker - 1
        # return

        # item = {
        #     "title": response.css("title::text").get(),
        #     "description": response.css(
        #         'meta[name="description"]::attr(content)'
        #     ).get(),
        # }
        # item["url"] = response.url
        # item["title"] = response.css("title::text").get()

        item = dp(OUT_TPL)
        if "results" not in data:
            return
        res = data["results"]
        title = [res["name"]]
        filters = {f["filter"]: f["title"] for f in res["filter_labels"]}
        descs = {
            f["code"]: f["values"][0]["name"]
            for f in res["description_blocks"]
            if f["type"] == "select"
        }

        if "cvet" in filters:
            title.append(filters["cvet"])
        if "obem" in filters:
            title.append(filters["obem"])
        brand = descs.get("brend", "")
        if not brand:
            brand = descs.get("proizvoditel", "")

        section = []
        cat = res["category"]
        if "name" in cat:
            section.append(cat["name"])
            if "parent" in cat:
                cat = cat["parent"]
                if "name" in cat:
                    section.append(cat["name"])
        section = section[::-1]

        # price
        price = res["price"]
        price_old = res["prev_price"]
        if price is None:
            price = 0
        if price_old is None:
            price_old = 0
        price = float(price)
        price_old = float(price_old)
        if not price_old:
            price_old = price
        price_discount = ""
        if price != price_old:
            price_discount = 100 - (price / price_old * 100)
            price_discount = f"Скидка {price_discount}%"

        in_stock = False
        count = int(res.get("quantity_total", 0))
        availability = res.get("availability")
        if "title" in availability and availability.get("title") == "Есть в наличии":
            in_stock = True
        stock = {"in_stock": in_stock, "count": count}

        # item["title"] = res[""][""][""][""]
        item["timestamp"] = int(time.time())
        item["RPC"] = res["vendor_code"]
        item["url"] = url
        item["title"] = ", ".join(title)
        item["marketing_tags"] = []
        item["brand"] = brand
        item["section"] = section
        item["assets"]["main_image"] = res["image_url"]

        prices = {}
        prices["current"] = price
        prices["original"] = price_old
        prices["sale_tag"] = price_discount
        item["price_data"] = prices
        item["stock"] = stock

        item["proxy"] = proxy
        self.logp(proxy, fg=31, bg=46)
        yield item

    # def closed(self, reason):
    #     v = self.crawler.stats.get_value("item_scraped_count")
    #     print(f'count: {v}')
    #     v = self.crawler.stats.get_value('item_scraped_count').values()
    #     # items = list(v)[0]
    #     items = self.crawler.stats.get_value('item_scraped_count')
    #     items = []
    #     filename = 'data.json'
    #     with open(filename, 'wb') as file:
    #         exporter = JsonItemExporter(file)
    #         exporter.start_exporting()
    #         for item in self.crawler.stats.get_value('items'):
    #             exporter.export_item(item)
    #         exporter.finish_exporting()
    #     self.log(f'Saved file {filename}, containing {items} items')
