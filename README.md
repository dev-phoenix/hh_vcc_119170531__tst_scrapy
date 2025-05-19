# test project for parser with scrapy
## hh vacancy 119170531 -- test scrapy parser

[![Coverage Status](https://coveralls.io/repos/github/dev-phoenix/hh_vcc_119170531__tst_scrapy/badge.svg?branch=master)](https://coveralls.io/github/dev-phoenix/hh_vcc_119170531__tst_scrapy?branch=master)
![GitHub repo size](https://img.shields.io/github/repo-size/dev-phoenix/hh_vcc_119170531__tst_scrapy)
<a href="https://github.com/dev-phoenix/hh_vcc_119170531__tst_scrapy/pulse" alt="Activity">
<img src="https://img.shields.io/github/commit-activity/m/dev-phoenix/hh_vcc_119170531__tst_scrapy" /></a>

[Scrapy v2.11 docs](https://docs.scrapy.org/en/2.11/)

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

### structured result:
```sh
# set debug=1 for filling result json with structured dump of items
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