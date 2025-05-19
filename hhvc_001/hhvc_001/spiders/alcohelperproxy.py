# alcohelperproxy.py
"""helper for AlcoSpider: Proxy"""

# from pathlib import Path
# from copy import deepcopy as dp
import json

# import urllib.parse as up
# import time
# import random
import re

# import logging

from bs4 import BeautifulSoup as bs
import scrapy

from hhvc_helper.hhvc_h_lib import HHVCSSHelper


class AlcoHelperProxy(HHVCSSHelper):
    """Helper for proxy from proxy5.net"""

    get_proxy_count = "1000"
    proxy_from = "proxy.json"
    proxy_on = False
    proxy_scenario = "json"

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
        _dt = re.search(r"(\{.*\})", res)
        data = _dt.group(0)
        # self.logp(data, fg=31)
        data = json.loads(data)
        nonce = data["nonce"]
        self.logp("nonce:", nonce, fg=31)
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
            # if self.proxy_list:
            #     proxy = random.choice(self.proxy_list)
            #     if self.is_dict(proxy):
            #         proxy = proxy["proxy"]
            #     proxy = f"{proxy}"
            #     print(proxy)
            #     # req.meta["proxy"] = proxy
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
        self.logp("parse_filter_proxy", "collect proxies")
        body = response.body.decode()
        print(body)

    def parse_filtered_proxy(self, response):
        """
        collect proxies
        """
        self.logp("proxylister_load_filtered", "collect proxies")
        # body = response.body.decode()
        # print(body)
        # data = json.loads(data)
        data = response.json()
        rows = data["data"]["rows"]
        # print(rows)
        soup = bs(f"<table>{rows}</table>", "html.parser")
        # self.logp(soup.title.string, fg=31)

        # nonce_script_id = "proxylister-js-js-extra"
        # script = soup.find("script", id=nonce_script_id)
        trs = soup.find_all("tr")
        # print(trs)
        for tr in trs:
            td = tr.find_all("td")
            # print(f'{tr}')
            ip = td[0].strong.string.strip()
            # print(f'{ip}')
            port = td[1].string.strip()
            country = tr.find(class_="country-name").strong
            city = country.next_sibling.next_sibling.string.strip()
            country = country.string.strip() + " - " + city
            print(f"{ip}:{port} -- {country}")
            proxy = {}
            proxy["ip"] = ip
            proxy["port"] = port
            proxy["proxy"] = f"{ip}:{port}"
            proxy["country"] = country
            yield proxy
