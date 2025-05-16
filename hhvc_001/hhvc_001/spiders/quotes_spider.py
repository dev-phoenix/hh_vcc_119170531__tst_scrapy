"""
quotes_spider.py
tz: https://docs.google.com/document/d/19mLRcZKbezZl9SCv709UcpcssFJycez6/edit?tab=t.0
"""
from pathlib import Path
from copy import deepcopy as dp
import json

import scrapy

# from scrapy.exporters import JsonItemExporter


CITY_SET = "Краснодар"
CITY_DEF = "Краснодар"
CITY_UUID_DEF = "4a70f9e0-46ae-11e7-83ff-00155d026416"

CITIES_URL = "https://alkoteka.com/web-api/v1/city?page={page}"

START_URLS = [
    "https://alkoteka.com/catalog/slaboalkogolnye-napitki-2",
    "https://alkoteka.com/catalog/slaboalkogolnye-napitki-2/\
options-vid_pivo-temnoe-filtrovannoe/options-vid_pivo-temnoe-nefiltrovannoe",
    "https://alkoteka.com/catalog/slaboalkogolnye-napitki-2/options-cena_400/options-cena_2990",
]

OUT_TPL = {
    "timestamp": 0,  # int,  # Дата и время сбора товара в формате timestamp.
    "RPC": "",  # "str",  # Уникальный код товара.
    "url": "",  # "str",  # Ссылка на страницу товара.
    "title": "",  # "str",  # Заголовок/название товара (! Если в карточке товара указан цвет или объем, но их нет в названии, необходимо добавить их в title в формате: "{Название}, {Цвет или Объем}").
    "marketing_tags": [],  # ["str"],  # Список маркетинговых тэгов, например: ['Популярный', 'Акция', 'Подарок']. Если тэг представлен в виде изображения собирать его не нужно.
    "brand": "",  # "str",  # Бренд товара.
    "section": [],  # ["str"],  # Иерархия разделов, например: ['Игрушки', 'Развивающие и интерактивные игрушки', 'Интерактивные игрушки'].
    "price_data": {
        "current": 0,  # float,  # Цена со скидкой, если скидки нет то = original.
        "original": 0,  # float,  # Оригинальная цена.
        "sale_tag": "",  # "str"  # Если есть скидка на товар то необходимо вычислить процент скидки и записать формате: "Скидка {discount_percentage}%".
    },
    "stock": {
        "in_stock": 0,  # bool,  # Есть товар в наличии в магазине или нет.
        "count": 0,  # int  # Если есть возможность получить информацию о количестве оставшегося товара в наличии, иначе 0.
    },
    "assets": {
        "main_image": "",  # "str",  # Ссылка на основное изображение товара.
        "set_images": [],  # ["str"],  # Список ссылок на все изображения товара.
        "view360": [],  # ["str"],  # Список ссылок на изображения в формате 360.
        "video": [],  # ["str"]  # Список ссылок на видео/видеообложки товара.
    },
    "metadata": {
        "__description": "",  # "str",  # Описание товара
        # "KEY": '', # "str",
        # "KEY": '', # "str",
        # "KEY": '', # "str"
        # Также в metadata необходимо добавить все характеристики товара которые могут быть на странице.
        # Например: Артикул, Код товара, Цвет, Объем, Страна производитель и т.д.
        # Где KEY - наименование характеристики.
    },
    "variants": 0,  # int,  # Кол-во вариантов у товара в карточке (За вариант считать только цвет или объем/масса. Размер у одежды или обуви варинтами не считаются).
}

TESTURL = """
https://alkoteka.com/web-api/v1/product
?city_uuid=4a70f9e0-46ae-11e7-83ff-00155d026416
&options%5Bcena%5D[]=400
&options%5Bcena%5D[]=2990
&page=1&per_page=20&root_category_slug=slaboalkogolnye-napitki-2
"""


TESTURL = """
https://alkoteka.com/web-api/v1/product
?city_uuid=4a70f9e0-46ae-11e7-83ff-00155d026416
&options%5Bvid%5D[]=pivo-temnoe-filtrovannoe
&options%5Bvid%5D[]=pivo-temnoe-nefiltrovannoe
&page=1&per_page=20&root_category_slug=slaboalkogolnye-napitki-2
"""

"""
https://alkoteka.com/web-api/v1/product
?city_uuid=4a70f9e0-46ae-11e7-83ff-00155d026416&page=4
&per_page=20&root_category_slug=slaboalkogolnye-napitki-2
"""


class QuotesSpider(scrapy.Spider):
    """
    hello world spider
    """

    name = "quotes"
    cities = {}
    cities_page = 1
    city_uuid = CITY_UUID_DEF

    async def start(self):
        """
        version: latest (v2.13)
        """
        self.start_requests()

    def start_requests(self):
        """
        version: v2.11
        """
        urls = [
            "https://quotes.toscrape.com/page/1/",
            "https://quotes.toscrape.com/page/2/",
            # "https://quotes.toscrape.com/page/1/",
            # "https://quotes.toscrape.com/page/2/",
        ]
        return self.getCities()

    def getCities(self):
        """
        collect cities uuid
        """
        url = CITIES_URL.format(page=self.cities_page)
        yield scrapy.Request(url=url, callback=self.parseCities)

    def parseCities(self, response):
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
            yield scrapy.Request(url=url, callback=self.parseCities)
        else:
            print("sites: ", self.cities)
            if CITY_SET in self.cities:
                self.city_uuid = self.cities[CITY_SET]
            urls = START_URLS
            for url in urls:
                print(f"catalog url: {url}")
                # print(scrapy.Request(url=url, callback=self.parseCatalog).body)
                yield scrapy.Request(url=url, callback=self.parseCatalog)

    def parse(self, response):
        """
        abstract method
        """
        ...

    def parseCatalog(self, response):
        """
        parse catalog pages
        """
        print(f"status: {response.status}")
        print(f"response: ", dir(response))
        page = response.url.split("/")[-2]
        filename = f"quotes-{page}.html"
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")

        item = {
            "title": response.css("title::text").get(),
            "description": response.css(
                'meta[name="description"]::attr(content)'
            ).get(),
        }
        item = dp(OUT_TPL)
        item["url"] = response.url
        item["title"] = response.css("title::text").get()
        yield item

        # next_page = response.css("li.next a::attr(href)").get()
        urls = response.css("li.next a::attr(href)").get()
        # for url in urls:
        #     print(f'item url: {url}')
        #     yield scrapy.Request(url=url, callback=self.parsePage)

    def parsePage(self, response):
        """
        parse item pages
        """
        print(f"status: {response.status}")
        page = response.url.split("/")[-2]
        filename = f"quotes-{page}.html"
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")

        item = {
            "title": response.css("title::text").get(),
            "description": response.css(
                'meta[name="description"]::attr(content)'
            ).get(),
        }
        item = dp(OUT_TPL)
        item["url"] = response.url
        item["title"] = response.css("title::text").get()
        yield item

    # def closed(self, reason):
    #     print(f'count: {self.crawler.stats.get_value("item_scraped_count")}')
    #     # items = list(self.crawler.stats.get_value('item_scraped_count').values())[0]
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
