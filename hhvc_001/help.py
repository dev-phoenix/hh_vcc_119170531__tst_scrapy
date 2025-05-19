# help.py
"""output help tips"""
from hhvc_helper.hhvc_h_lib import HHVCSSHelper
# from hhvc_001.hhvc_helper.hhvc_h_lib import HHVCSSHelper # if from root
from hhvc_001.spiders.params import CITY_SET, CITY_DEF, CITY_UUID_DEF, CITIES_URL, START_URLS

class Help(HHVCSSHelper):
    """helper for output help tips"""
    def __init__(self, tips: list = None):
        super().__init__()
        self.tips = tips
        self.print_tips()

    def print_tips(self):
        if not self.tips:
            self.logp('No tips.')
            return
        for tip in self.tips:
            self.logp(tip)

TIP_1 = """\
# to choce city (default: Краснодар)
scrapy crawl alco -O result.json -a city=Москва\
"""

TIP_2 = """\
# to choce catalog url list. catalog.txt contains one url per row.
scrapy crawl alco -O result.json -a catalogs_file=catalog.txt\
"""

TIP_3 = """\
# set limit for result count. (default: 10; all: 0)
scrapy crawl alco -O result.json -a product_count=2\
"""

TIP_3_1 = """\
# set debug=1 for filling result json with structured dump of items
scrapy crawl alco -O result.json -a product_count=2 -a debug=1\
"""

TIP_4 = """\
# collect proxy from ://proxy5.net (work only with http, not https:( )
scrapy crawl alco -O proxy.json -a scenario=proxy

# run crawler with collected proxy
scrapy crawl alco -O result.json -a proxy_on=on\
"""

TIP_5 = """\
# collect proxy with chiced count (default: 1000)
scrapy crawl alco -O proxy.json -a scenario=proxy -a proxy_count=10\
"""

TIP_6 = """\
# check live proxy for https. from proxy.json to proxy_filtered_3.json
python3 proxy_checker.py

# run crawler with filtered proxy
scrapy crawl alco -O result.json -a proxy_on=on -a proxy_from=proxy_filtered_3.json\
"""

TIP_7 = """\
# proxy txt file must containing on proxy per row.
# skip rows started with "#"
scrapy crawl alco -O result.json -a proxy_on=on -a proxy_from=proxy.txt\
"""

HELP_TIPS = []
# HELP_TIPS.append(CITY_SET)
HELP_TIPS.append(TIP_1)
HELP_TIPS.append(TIP_2)
HELP_TIPS.append(TIP_3)
HELP_TIPS.append(TIP_4)
HELP_TIPS.append(TIP_5)
HELP_TIPS.append(TIP_6)
HELP_TIPS.append(TIP_7)

if __name__ == "__main__":
    try:
        helper = Help(HELP_TIPS)
    except KeyboardInterrupt:
        print('Bye.')
    except Exception as e:
        print(e)