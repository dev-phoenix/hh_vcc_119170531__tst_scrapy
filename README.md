# test project for parser with scrapy
## hh vacancy 119170531 -- test scrapy parser

[![Coverage Status](https://coveralls.io/repos/github/dev-phoenix/hh_vcc_119170531__tst_scrapy/badge.svg?branch=master)](https://coveralls.io/github/dev-phoenix/hh_vcc_119170531__tst_scrapy?branch=master)
![GitHub repo size](https://img.shields.io/github/repo-size/dev-phoenix/hh_vcc_119170531__tst_scrapy)
<a href="https://github.com/dev-phoenix/hh_vcc_119170531__tst_scrapy/pulse" alt="Activity">
<img src="https://img.shields.io/github/commit-activity/m/dev-phoenix/hh_vcc_119170531__tst_scrapy" /></a>

[Scrapy v2.11 docs](https://docs.scrapy.org/en/2.11/)

## major structure:
```sh
hhvc_001/
| hhvc_001/
| | spiders/
| | + alco_spider.py # main spider script
| | + alcohelpercities.py # collect cities
| | + alcohelperproxy.py # collect free proxy
| | + params.py # contain variable with catalogs list for collecting urls
| | hhvc_helper/
| | | + hhvc_h_lib.py # helper methods for main script
| | | + models.py # containg main data structure for output
| + proxy.txt # simple plain list with proxies
```

### features:
- **Takes catalog urls from attribute or file**
- **Parsing free proxy list**
- **Alternatively: Takes simple plain proxy list from txt file**
- **On/Off using proxy by seting from running comand line**
- **Automaticly parsing uuid list for choice city**
- **Using orher choiced city**

### catalog urls:
file `hhvc_001/hhvc_001/spiders/alco_spider.py`  
contains attribute `start_url` with list of catalogs for collectin product urls  
If it's not existts or empty  
urls will takes from variable `START_URLS` located on file:  
`hhvc_001/hhvc_001/spiders/params.py`  

### default city:
If it's containg in variable `CITY_SET` located on file:  
`hhvc_001/hhvc_001/spiders/params.py`  

### to start:
```sh
git clone https://github.com/dev-phoenix/hh_vcc_119170531__tst_scrapy.git
cd hh_vcc_119170531__tst_scrapy/
pip -m venv .env
. ./.env/bin/activate

# pip install wheel # if needed

# import requirements
pip install -r requirements.txt

cd hhvc_001
# spiders list
scrapy list

# run crawler
scrapy crawl alco -O result.json
```

### settings:
All available main settings of spider  
placed in [hhvc_001/hhvc_001/spiders/params.py](hhvc_001/hhvc_001/spiders/params.py)

### help on linux:
```sh
# shows following below tips
. help
```

### city choice:
```sh
# to choce city (default: Краснодар)
scrapy crawl alco -O result.json -a city=Москва
```

### catalogs choice:
```sh
# to choce catalog url list. catalog.txt contains one url per row.
scrapy crawl alco -O result.json -a catalogs_file=catalog.txt
```

### parse limit:
```sh
# set limit for result count. (default: 10; all: 0)
scrapy crawl alco -O result.json -a product_count=2
```

### debug:
```sh
# set debug=1 for more debugging
scrapy crawl alco -O result.json -a product_count=2 -a debug=1
```

### run with proxy:
```sh
# collect proxy from ://proxy5.net (work only with http, not https:( )
scrapy crawl alco -O proxy.json -a scenario=proxy

# run crawler with collected proxy
scrapy crawl alco -O result.json -a proxy_on=on
```

### set limit of collected proxy:
```sh
# collect proxy with chiced count (default: 1000)
scrapy crawl alco -O proxy.json -a scenario=proxy -a proxy_count=10
```

### run with filtered proxy:
```sh
# check live proxy for https. from proxy.json to proxy_filtered_3.json
python3 proxy_checker.py

# run crawler with filtered proxy
scrapy crawl alco -O result.json -a proxy_on=on -a proxy_from=proxy_filtered_3.json
```

### run with proxy in txt file:
```sh
# proxy txt file must containing on proxy per row.
# skip rows started with "#"
scrapy crawl alco -O result.json -a proxy_on=on -a proxy_from=proxy.txt
```

### be carefully by loading unknown files !!!