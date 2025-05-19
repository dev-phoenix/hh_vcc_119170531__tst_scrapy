# proxy_ckecker.py
"""Allows to check proxy list for available proxies"""

import json
import logging
import urllib
from pathlib import Path
import urllib.request
import http

from bs4 import BeautifulSoup as bs

log = logging.getLogger("scrapy.proxies")
logging.basicConfig(filename="proxies.log", level=logging.DEBUG)


class ParserTs:
    """
    Allows to check proxy list for available proxies
    """

    # proxy
    # https://proxy5.net/ru/free-proxy
    proxy_list = []
    proxy_list_filtered = []
    out_name = "proxy_filtered.json"
    file_name: str = "proxy.json"
    url_checker = "https://alkoteka.com/catalog/slaboalkogolnye-napitki-2"
    url_checker = "https://alkoteka.com/product/pivo-1/flensburger-pilsner_68231"
    url_checker = """\
https://alkoteka.com/web-api/v1/product/flensburger-pilsner_68231\
?city_uuid=4a70f9e0-46ae-11e7-83ff-00155d026416\
"""
    schema_checker = 'https'
    url_checker = "http://whatismyipaddress.com/"
    url_checker = "https://www.showmyip.com/"
    url_checker = "://www.showmyip.com/"
    fail = 0
    ok = 0
    error = 0
    timeout = 5

    def __init__(self, *args, schema_checker = None, **kwargs):
        if schema_checker and schema_checker in ['http', 'https']:
            self.schema_checker = schema_checker
        if "schema" in kwargs:
            self.schema_checker = kwargs["schema"]
        if "from_name" in kwargs:
            self.file_name = kwargs["from_name"]
        if "to" in kwargs:
            self.out_name = kwargs["to"]

    def logp(self, *args, **kwargs):
        """colored print"""
        fg = kwargs.get("fg", 30)
        bg = kwargs.get("bg", 47)
        if "fg" in kwargs:
            del kwargs["fg"]
        if "bg" in kwargs:
            del kwargs["bg"]
        print()
        print(f"\033[1;{fg};{bg}m", *args, "\033[0m", **kwargs)

    def load_proxy(self, file_name: str = "proxy.json") -> None:
        """Load proxies from file"""
        if not file_name:
            file_name = self.file_name
        # json_proxy = Path(file_name).read()
        with open(file_name, "r", encoding="utf-8") as file:
            data = json.load(file)
            for p in data:
                self.proxy_list.append(p)
                mess = f'Proxy : {p["proxy"]} {p["country"]}'
                log.debug(mess)
                self.logp("from url:", mess, fg=31)
    
    def mess_time_needed(self, pcou):
        """statistic message"""
        timeout = int(self.timeout)
        # pcou = len(self.proxy_list)
        to_seconds = timeout * pcou
        minuts = to_seconds//60
        to_seconds -= minuts * 60
        hours = minuts//60
        minuts -= hours * 60
        time_needed = f'{hours} hours, {minuts} minuts, {to_seconds} seconds,'
        if hours == 0:
            time_needed = f'{minuts} minuts, {to_seconds} seconds,'
        if hours == 0 and minuts == 0:
            time_needed = f'{to_seconds} seconds,'
        time_needed = f'{hours:02d}:{minuts:02d}:{to_seconds:02d}'
        self.logp(f'time needed: {time_needed} in queue: {pcou} filtered: {self.ok}', fg=32, bg=40)

    def check(self):
        """check proxies for living"""
        log.info("Started")
        url_checker = f"{self.schema_checker}{self.url_checker}"
        self.logp('url for check:', url_checker, fg=32, bg=40)
        self.logp('schema:', self.schema_checker, fg=32, bg=40)
        self.logp('from:', self.file_name, fg=32, bg=40)
        self.logp('to:', self.out_name, fg=32, bg=40)
        pcou = len(self.proxy_list)
        pcou_2 = pcou
        self.mess_time_needed(pcou_2)
        self.logp(f'cou to check: {pcou}; ', fg=31)
        # self.proxy_list = self.proxy_list[::-1]
        for p in self.proxy_list:
            print()
            print('-'*10)
            proxy = p["proxy"]
            try:
                # # urllib.urlopen(
                # #     "http://example.com",
                # #     proxies={'http':'http://example.com:8080'}
                # # )
                # urllib.urlopen(
                #         self.url_checker,
                #         proxies={'http':'http://example.com:8080'}
                #     )

                ph = {}
                ph['http'] = proxy
                ph['https'] = proxy
                proxy_handler = urllib.request.ProxyHandler(ph)
                opener = urllib.request.build_opener(proxy_handler)
                urllib.request.install_opener(opener)
                request = urllib.request.Request(
                    url_checker, headers={"User-Agent": "Tester"}
                )

                response = urllib.request.urlopen(
                    request, timeout=self.timeout
                    ).read().decode("utf-8")
                # print(dir(response))
                # body = response.body.decode()
                body = response
                # print(body)
                soup = bs(body, "html.parser")
                # self.logp(soup.title, fg=31)
                # self.logp(soup.title.string, fg=31)
                if soup.h2:
                    ip = soup.h2.string
                else:
                    ip = '- '*5
                    self.logp('my ip:', ip, fg=31)
                    raise Exception('no data')
                self.logp('my ip:', ip, fg=31)
                # self.logp(soup.title, fg=31)
            # except IOError:
            except (
                urllib.request.URLError,
                urllib.request.HTTPError,
                http.client.HTTPException,
            ) as e:
                mess = f'Filed : {p["proxy"]} {p["country"]}'
                self.logp(mess, fg=37, bg=41)
                url_checker = f"{self.schema_checker}{self.url_checker}"
                self.logp(url_checker, fg=31)
                self.fail +=1
            except Exception as e:
                mess = f'Error : {p["proxy"]} {p["country"]}'
                self.logp(mess, '|', e, fg=37, bg=41)
                self.error +=1
            else:
                self.proxy_list_filtered.append(p)
                mess = f'Passed : {p["proxy"]} {p["country"]}'
                self.logp(mess, fg=30, bg=42)
                self.ok +=1
            pcou_2 -= 1
            self.mess_time_needed(pcou_2)
        log.info("Finished")

    def save(self, out_name = False):
        """save filtered proxies to file"""
        print()
        print('-' * 30)
        if not out_name:
            out_name = self.out_name
        self.logp(f'pass: {self.ok}; fail: {self.fail}; error: {self.error}; ', fg=31)
        self.logp(f'save: {len(self.proxy_list_filtered)}; ', fg=31)
        with open(out_name, 'w') as file:
            file.write("[\n")
            out = []
            for p in self.proxy_list_filtered:
                out.append( json.dumps(p) )
            file.write(",\n".join(out))
            file.write("\n]")
        # out = json.dumps(self.proxy_list_filtered)
        # Path(out_name).write_text(out)
        print()


if __name__ == "__main__":
    try:
        from_name ="proxy_filtered.json"
        to_name = "proxy_filtered_2.json"

        from_name ="proxy.json"
        to_name = "proxy_filtered_2.json"

        from_name ="proxy.json"
        to_name = "proxy_filtered_3.json"

        schema = 'https'
        schema = 'http'
        pts = ParserTs(schema=schema, from_name=from_name, to=to_name)
        pts.load_proxy()
        pts.check()
        pts.save()

        # while True:
        #     # maxchoice = 7
        #     # print(vars)
        #     inptpl = "Select your choice\n"
        #     way = input(inptpl)
        #     if way == "":
        #         way = 3
        #     print(f"You'r choice is: {way}")
        #     # way = int(way)
        #     # if way < 1 or way > maxchoice:
        #     #     raise KeyboardInterrupt("Result out of range")
        #     # kaggle_test(way)
        print("Bye.-----------------")
    except KeyboardInterrupt as e:
        print(e)
        print("Bye.")
    except ValueError as e:
        print(e)
        print("Result not numeric")
        print("Bye.")
