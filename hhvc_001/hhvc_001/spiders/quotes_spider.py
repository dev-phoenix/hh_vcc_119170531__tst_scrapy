"""
quotes_spider.py
tz: https://docs.google.com/document/d/\
19mLRcZKbezZl9SCv709UcpcssFJycez6/edit?tab=t.0
"""
from pathlib import Path
from copy import deepcopy as dp
import json
import urllib.parse as up

import scrapy

# from scrapy.exporters import JsonItemExporter


CITY_SET = "Краснодар"
CITY_SET = "Москва"
CITY_DEF = "Краснодар"
CITY_UUID_DEF = "4a70f9e0-46ae-11e7-83ff-00155d026416"

CITIES_URL = "https://alkoteka.com/web-api/v1/city?page={page}"

START_URLS = [
    "https://alkoteka.com/catalog/slaboalkogolnye-napitki-2",
    "https://alkoteka.com/catalog/slaboalkogolnye-napitki-2/\
options-vid_pivo-temnoe-filtrovannoe/\
options-vid_pivo-temnoe-nefiltrovannoe",
    "https://alkoteka.com/catalog/slaboalkogolnye-napitki-2/\
options-cena_400/options-cena_2990",
]

OUT_TPL = {
    "timestamp": 0,  # int,  # Дата и время сбора товара в формате timestamp.
    "RPC": "",  # "str",  # Уникальный код товара.
    "url": "",  # "str",  # Ссылка на страницу товара.
    "title": "",  # "str",
    # Заголовок/название товара (! Если в карточке товара указан цвет
    # или объем, но их нет в названии, необходимо добавить их в title
    # в формате: "{Название}, {Цвет или Объем}").
    "marketing_tags": [],  # ["str"],
    # Список маркетинговых тэгов, например:
    # ['Популярный', 'Акция', 'Подарок'].
    # Если тэг представлен в виде изображения собирать его не нужно.
    "brand": "",  # "str",  # Бренд товара.
    "section": [],  # ["str"],
    # Иерархия разделов, например:
    # ['Игрушки', 'Развивающие и интерактивные игрушки',
    # 'Интерактивные игрушки'].
    "price_data": {
        "current": 0,  # float,
        # Цена со скидкой, если скидки нет то = original.
        "original": 0,  # float,  # Оригинальная цена.
        "sale_tag": "",  # "str"
        # Если есть скидка на товар то необходимо вычислить процент скидки
        # и записать формате: "Скидка {discount_percentage}%".
    },
    "stock": {
        "in_stock": 0,  # bool,  # Есть товар в наличии в магазине или нет.
        "count": 0,  # int
        # Если есть возможность получить информацию о количестве
        # оставшегося товара в наличии, иначе 0.
    },
    "assets": {
        "main_image": "",  # "str",  # Ссылка на основное изображение товара.
        "set_images": [],  # ["str"],
        # Список ссылок на все изображения товара.
        "view360": [],  # ["str"],
        # Список ссылок на изображения в формате 360.
        "video": [],  # ["str"]  # Список ссылок на видео/видеообложки товара.
    },
    "metadata": {
        "__description": "",  # "str",  # Описание товара
        # "KEY": '', # "str",
        # "KEY": '', # "str",
        # "KEY": '', # "str"
        # Также в metadata необходимо добавить все характеристики товара
        # которые могут быть на странице.
        # Например:
        # Артикул, Код товара, Цвет, Объем, Страна производитель и т.д.
        # Где KEY - наименование характеристики.
    },
    "variants": 0,  # int,
    # Кол-во вариантов у товара в карточке
    # (За вариант считать только цвет или объем/масса.
    # Размер у одежды или обуви варинтами не считаются).
}

TESTURL = """
https://alkoteka.com/web-api/v1/product
?city_uuid=4a70f9e0-46ae-11e7-83ff-00155d026416
&options%5Bcena%5D[]=400
&options%5Bcena%5D[]=2990
&page=1&per_page=20&root_category_slug=slaboalkogolnye-napitki-2
"""


TESTURL = """\
https://alkoteka.com/web-api/v1/product\
?city_uuid=4a70f9e0-46ae-11e7-83ff-00155d026416\
&options%5Bvid%5D[]=pivo-temnoe-filtrovannoe\
&options%5Bvid%5D[]=pivo-temnoe-nefiltrovannoe\
&page=1&per_page=20&root_category_slug=slaboalkogolnye-napitki-2\
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
    city_name = CITY_DEF
    city_uuid = CITY_UUID_DEF
    product_urls = []

    async def start(self):
        """
        version: latest (v2.13)
        """
        self.start_requests()

    def start_requests(self):
        """
        version: v2.11
        """
        # urls = [
        #     "https://quotes.toscrape.com/page/1/",
        #     "https://quotes.toscrape.com/page/2/",
        #     # "https://quotes.toscrape.com/page/1/",
        #     # "https://quotes.toscrape.com/page/2/",
        # ]
        # url = CITIES_URL.format(page=self.cities_page)
        # yield scrapy.Request(url=url, callback=self.parse)
        return self.get_cities()

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
            if CITY_SET in self.cities:
                self.city_uuid = self.cities[CITY_SET]
                self.city_name = CITY_SET
            print("\033[1;30;1;47mselected location:", self.city_name, self.city_uuid, "\033[0m")

            # collect category products
            urls = START_URLS
            for url in urls:
                url = self.url_to_rest(url, page=1)
                self.logp(f"catalog url: {url}")
                # print(scrapy.Request(
                # url=url, callback=self.parse_catalog).body)
                yield scrapy.Request(url=url, callback=self.parse_catalog)

    def parse(self, response, **kwargs):
        """
        abstract method
        """
        b = False
        if b:
            print('parse')
            print(response)
        yield 'item'

    def logp(self, *args, **kwargs):
        """colored print
        """
        fg = kwargs.get('fg',30)
        bg = kwargs.get('bg',47)
        if 'fg' in kwargs:
            del kwargs['fg']
        if 'bg' in kwargs:
            del kwargs['bg']
        print()
        print(f"\033[1;{fg};1;{bg}m", *args, "\033[0m", **kwargs)


    def url_to_rest(self, url: str, **kwargs: dict)->str:
        """convert public url to json request url
        """
        if 'web-api' in url:
            return url

        gate = 'https://alkoteka.com/web-api/v1/'
        ptype = 'product'
        cuuid = self.city_uuid
        page = kwargs.get('page', 1)
        per_page = kwargs.get('per_page', 100)
        curl = url.replace('https://','')
        curl = curl.replace('http://','')
        curl = curl.split('/')

        opts = []
        opts.append(('city_uuid', cuuid))

        if curl[1] == 'catalog':
            catalog = curl[2]
            _opts = curl[3:]
            _opts = self.url_opts_parse(_opts)
            opts.extend(_opts)
            opts.append(('page', f'{page}'))
            opts.append(('per_page', f'{per_page}'))
            opts.append(('root_category_slug', f'{catalog}'))

        self.logp('from url:', url, fg=31)
        self.logp('curl:', curl)
        self.logp('opts:', opts)

        opts = up.urlencode(opts)
        url = f'{gate}{ptype}?{opts}'

        return url


    def url_opts_parse(self, opts: list) -> list:
        """Build options query dict
        """
        _opts = []
        for opt in opts:
            if opt.startswith('options'):
                opt = opt.split('_')
                key = f"options[{opt[0].split('-')[1]}][]"
                # if key not in _opts:
                #     _opts[key] = []
                _opts.append((key, opt[1]))
        return _opts


    def url_page_increment(self, url:str) -> str:
        """create url for next page
        """
        url = up.urlparse(url)
        opts = up.parse_qsl(url.query)
        self.logp('url_page_increment', opts, fg=34)
        _opts = []
        for opt in opts:
            if opt[0] == 'page':
                # opt[1] = int(opt[1]) + 1
                tap = (opt[0], int(opt[1]) + 1)
                _opts.append(tap)
            else:
                _opts.append(opt)
        # page = int(opts['page'])
        # opts['page'] = page + 1
        opts = up.urlencode(_opts)
        self.logp('urlencode', opts)
        url = url._replace(query=opts)
        url = up.urlunparse(url)
        self.logp('url_page_increment url', url, fg=35)
        return url


    def parse_catalog(self, response):
        """
        parse catalog pages
        """
        print(f"status: {response.status}")
        print("response: ", dir(response))

        url = response.url
        self.logp("url:", url, fg=31, bg=46)

        data = response.json()
        # print("data: ", data)

        self.product_urls.extend(res['product_url'] for res in data['results'])
        self.log("\033[1;30;1;47mproducts count:"\
                + str(len(self.product_urls)) + "\033[0m")

        if data['meta']['has_more_pages'] :
            url = self.url_page_increment(url)
            self.logp(f"parse catalog url: {url}")
            self.log("\033[1;30;1;47mcatalog url:" + url + "\033[0m")
            # print(scrapy.Request(
            # url=url, callback=self.parse_catalog).body)
            yield scrapy.Request(url=url, callback=self.parse_catalog)

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

    def parse_page(self, response):
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
