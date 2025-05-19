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
import re
import logging

from bs4 import BeautifulSoup as bs
import scrapy
# from scrapy.exporters import JsonItemExporter

log = logging.getLogger('scrapy.proxies')

# set location
CITY_SET = "Москва"
CITY_SET = "Краснодар"

# default location
CITY_DEF = "Краснодар"
CITY_UUID_DEF = "4a70f9e0-46ae-11e7-83ff-00155d026416"

# template for collecting locations
CITIES_URL = "https://alkoteka.com/web-api/v1/city?page={page}"

# array with catalog urls
START_URLS = [
    "https://alkoteka.com/catalog/slaboalkogolnye-napitki-2",
    "https://alkoteka.com/catalog/slaboalkogolnye-napitki-2/\
options-vid_pivo-temnoe-filtrovannoe/\
options-vid_pivo-temnoe-nefiltrovannoe",
    "https://alkoteka.com/catalog/slaboalkogolnye-napitki-2/\
options-cena_400/options-cena_2990",
]

# template for output items
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

# exemples of json request
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

TESTURL = """
https://alkoteka.com/web-api/v1/product
?city_uuid=4a70f9e0-46ae-11e7-83ff-00155d026416&page=4
&per_page=20&root_category_slug=slaboalkogolnye-napitki-2
"""

TESTURL = """
https://alkoteka.com/product/pivo-1/shtefans-brau-shvarcbir_29300
=>
https://alkoteka.com/web-api/v1/product/shtefans-brau-shvarcbir_29300
?city_uuid=985b3eea-46b4-11e7-83ff-00155d026416

https://alkoteka.com/web-api/v1/product/
pivnoy-napitok-ganza-goze-tomato-journey-smoked_98103
?city_uuid=396df2b5-7b2b-11eb-80cd-00155d039009

https://alkoteka.com/web-api/v1/product/velkopopovickiy-kozel-svetlyy_91167
?city_uuid=396df2b5-7b2b-11eb-80cd-00155d039009
"""


class AlcoSpider(scrapy.Spider):
    """
    hello world spider
    transformed for tecnical tasks
    """

    name = "alco"

    custom_settings = {
        "DOWNLOAD_DELAY": 0.25,  # 250 ms of delay
    }

    cities = {}
    cities_page = 1
    city_choice = CITY_SET
    city_name = CITY_DEF
    city_uuid = CITY_UUID_DEF
    product_urls = {}
    catalog_parsed_count = 0
    catalog_urls = []
    catalogs_file = False

    max_result = 10
    get_proxy_count = "1000"
    proxy_from = "proxy.json"
    proxy_on = False
    proxy_scenario = "json"

    # proxy
    # https://proxy5.net/ru/free-proxy
    proxy_list = []

    scenario = "get proxy"

    def __init__(
            self, *args,
            scenario = None, proxy_from = None,
            proxy_count = None, proxy_on = None,
            city = None, catalogs_file = None,
            **kwargs
            ):
        """
        initialization
        """
        super(AlcoSpider, self).__init__(*args, **kwargs)
        # super(*args, **kwargs)
        if scenario == 'proxy':
            self.scenario = 'get proxy'
        else:
            self.scenario = 'get alco'
        if proxy_from:
            self.proxy_from = proxy_from
            ext = self.proxy_from.split('.')[-1]
            proxy_scenario = ext
        if proxy_count:
            try:
                proxy_count = int(proxy_count)
            except:
                ...
            else:
                self.get_proxy_count = str(proxy_count)
        if proxy_on in ['on', 'off'] and proxy_on == 'on':
            self.proxy_on = True

        self.city_choice = CITY_SET
        if city:
            self.city_choice = city
        if catalogs_file:
            self.catalogs_file = catalogs_file
        
    def collect_catalogs(self):
        self.catalog_urls = START_URLS
        if not self.catalogs_file:
            return
        self.catalog_urls = []
        with open(self.catalogs_file, 'r', encoding="utf-8") as file:
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

    def load_proxy(self, file_name: str = 'proxy.json') -> None:
        """Load proxies from file"""

        # json_proxy = Path(file_name).read()
        with open(file_name, 'r', encoding="utf-8") as file:
            data = json.load(file)
            if self.proxy_scenario == "txt":
                data = []
                for row in file:
                    if row:
                        data.append(row)
            for p in data:
                if self.is_dict(p):
                    p = p['proxy']
                self.proxy_list.append(p['proxy'])

    def get_proxy(self):
        """
        get proxies
        """
        self.logp("get proxies")
        # params = {}
        url = "https://proxy5.net/ru/wp-admin/admin-ajax.php"
        url = "https://proxy5.net/ru/free-proxy"
        req_args = {}
        req_args["url"] = url
        req_args["callback"] = self.parse_proxy_get_nonce
        # nonce = ""
        # req_args['method'] = 'POST'
        # req_args['body'] = {'action':'proxylister_load_filtered',
        # 'nonce':nonce,'filter[protocols]':'HTTP',
        # 'filter[anonymity]':'Anonymous','filter[latency]':'',
        # 'filter[page_size]':'20',}
        self.logp("req_args:", req_args)
        yield scrapy.Request(**req_args)
    
    def is_dict(self, obj):
        return obj.__class__.__name__ == 'dict'
    
    def is_list(self, obj):
        return obj.__class__.__name__ == 'list'
    
    def is_str(self, obj):
        return obj.__class__.__name__ == 'str'

    def parse_proxy_get_nonce(self, response):
        """
        collect proxy nonce
        """
        self.logp("collect proxy nonce")
        body = response.body.decode()
        # print(body)
        soup = bs(body, "html.parser")
        self.logp(soup.title.string, fg=31)

        nonce_script_id = "proxylister-js-js-extra"
        script = soup.find("script", id=nonce_script_id)
        # self.logp(script, fg=31)
        res = script.prettify()
        # print(res)
        _dt = re.search(r'(\{.*\})', res)
        data = _dt.group(0)
        # self.logp(data, fg=31)
        data = json.loads(data)
        nonce = data['nonce']
        self.logp('nonce:', nonce, fg=31)
        # ret = {'nonce': nonce}
        # yield ret

        # nonce_script_id = 'proxylister-js-js-extra'
        # script = soup.find('script', id = nonce_script_id)
        # print(script.prettyfy())

        urls = [
            "https://proxy5.net/ru/free-proxy",
            "https://proxy5.net/ru/wp-admin/admin-ajax.php",
        ]
        url = urls[0]
        req_args = {}
        # nonce = ""
        if nonce:
            req_args["method"] = "POST"
            req_args["formdata"] = {  # body
                "action": "proxylister_load_filtered",
                "nonce": nonce,
                "filter[protocols]": "HTTP",
                "filter[anonymity]": "Anonymous",
                "filter[latency]": "",
                "filter[page_size]": self.get_proxy_count,
            }
            # req_args["body"] = json.dumps(req_args["body"])
            # req_args["headers"] = {'Content-Type':'application/json'}
            url = urls[1]
            req_args["url"] = url
            req_args["callback"] = self.parse_filtered_proxy
            self.logp("req_args:", req_args)
            req = scrapy.FormRequest(**req_args)
            # req = scrapy.Request(url=url, callback=self.parse_page)
            if self.proxy_list:
                proxy = random.choice(self.proxy_list)
                if self.is_dict(proxy):
                    proxy = proxy['proxy']
                proxy = f'{proxy}'
                print(proxy)
                # req.meta["proxy"] = proxy
            yield req
        else:
            req_args["url"] = url
            req_args["callback"] = self.parse_proxy
            self.logp("req_args:", req_args)
            yield scrapy.Request(**req_args)

    def parse_proxy(self, response):
        """
        collect proxies
        """
        self.logp('parse_filter_proxy', "collect proxies")
        body = response.body.decode()
        print(body)

    def parse_filtered_proxy(self, response):
        """
        collect proxies
        """
        self.logp('proxylister_load_filtered', "collect proxies")
        # body = response.body.decode()
        # print(body)
        # data = json.loads(data)
        data = response.json()
        rows = data['data']['rows']
        # print(rows)
        soup = bs(f"<table>{rows}</table>", "html.parser")
        # self.logp(soup.title.string, fg=31)

        # nonce_script_id = "proxylister-js-js-extra"
        # script = soup.find("script", id=nonce_script_id)
        trs = soup.find_all("tr")
        # print(trs)
        for tr in trs:
            td = tr.find_all('td')
            # print(f'{tr}')
            ip = td[0].strong.string.strip()
            # print(f'{ip}')
            port = td[1].string.strip()
            country = tr.find(class_="country-name").strong
            city = country.next_sibling.next_sibling.string.strip()
            country = country.string.strip() + ' - ' + city
            print(f'{ip}:{port} -- {country}')
            proxy = {}
            proxy['ip'] = ip
            proxy['port'] = port
            proxy['proxy'] = f'{ip}:{port}'
            proxy['country'] = country
            yield proxy

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
            print("parse")
            print(response)
        yield "item"

    def logp(self, *args, **kwargs):
        """colored print"""
        fg = kwargs.get("fg", 30)
        bg = kwargs.get("bg", 47)
        if "fg" in kwargs:
            del kwargs["fg"]
        if "bg" in kwargs:
            del kwargs["bg"]
        print()
        print(f"\033[1;{fg};1;{bg}m", *args, "\033[0m", **kwargs)

    def url_to_rest(self, url: str, **kwargs: dict) -> str:
        """convert public url to json request url"""
        if "web-api" in url:
            return url

        gate = "https://alkoteka.com/web-api/v1/"
        ptype = "product"
        product = ""
        cuuid = self.city_uuid
        page = kwargs.get("page", 1)
        per_page = kwargs.get("per_page", 100)
        curl = url.replace("https://", "")
        curl = curl.replace("http://", "")
        curl = curl.split("/")

        opts = []
        opts.append(("city_uuid", cuuid))

        if curl[1] == "catalog":
            catalog = curl[2]
            _opts = curl[3:]
            _opts = self.url_opts_parse(_opts)
            opts.extend(_opts)
            opts.append(("page", f"{page}"))
            opts.append(("per_page", f"{per_page}"))
            opts.append(("root_category_slug", f"{catalog}"))

        if curl[1] == "product":
            product = curl[-1]

        self.logp("from url:", url, fg=31)
        # self.logp('curl:', curl)
        # self.logp('opts:', opts)

        opts = up.urlencode(opts)
        url = f"{gate}{ptype}/{product}?{opts}"

        return url

    def url_opts_parse(self, opts: list) -> list:
        """Build options query dict"""
        _opts = []
        for opt in opts:
            if opt.startswith("options"):
                opt = opt.split("_")
                key = f"options[{opt[0].split('-')[1]}][]"
                # if key not in _opts:
                #     _opts[key] = []
                _opts.append((key, opt[1]))
        return _opts

    def url_page_increment(self, url: str) -> str:
        """create url for next page"""
        url = up.urlparse(url)
        opts = up.parse_qsl(url.query)
        # self.logp('url_page_increment', opts, fg=34)
        _opts = []
        for opt in opts:
            if opt[0] == "page":
                tap = (opt[0], int(opt[1]) + 1)
                _opts.append(tap)
            else:
                _opts.append(opt)
        opts = up.urlencode(_opts)
        # self.logp('urlencode', opts)
        url = url._replace(query=opts)
        url = up.urlunparse(url)
        self.logp("url_page_increment url", url, fg=35)
        return url

    def parse_catalog(self, response):
        """
        parse catalog pages
        """
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
            self.product_urls[name] = {'url': res["product_url"]}
        pcou = len(self.product_urls)
        self.log(f"\033[1;30;1;47mproducts count: {pcou}\033[0m")

        if data["meta"]["has_more_pages"]:
            url = self.url_page_increment(url)
            self.logp(f"parse catalog url: {url}")
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
            if self.catalog_parsed_count == len(self.catalog_urls):
                # collect products data
                urls = self.product_urls
                max_result = self.max_result
                for name, url in urls.items():
                    if max_result == 0:
                        break
                    max_result -= 1
                    url = url['url']
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
                            proxy = proxy['proxy']
                        # proxy = f'https://{proxy}'
                        proxy = f'{proxy}'
                        print(proxy)
                        req.meta["proxy"] = proxy
                        # path = up.urlparse(response.url).path
                        # name = path.split("/")[-1]
                        self.product_urls[name]['proxy'] = proxy
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
        """
        parse item pages
        """
        print(f"status: {response.status}")
        path = up.urlparse(response.url).path
        name = path.split("/")[-1]
        url = self.product_urls[name]["url"]
        proxy = self.product_urls[name]['proxy']
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
        brand = descs.get("proizvoditel", "")

        # item["title"] = res[""][""][""][""]
        item["timestamp"] = int(time.time())
        item["RPC"] = res["vendor_code"]
        item["url"] = url
        item["title"] = ", ".join(title)
        item["brand"] = brand
        item["assets"]["main_image"] = res["image_url"]
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
