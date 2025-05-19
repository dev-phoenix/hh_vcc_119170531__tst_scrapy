# test project for parser with scrapy
## hh vacancy 119170531 -- test scrapy parser

[![Coverage Status](https://coveralls.io/repos/github/dev-phoenix/hh_vcc_119170531__tst_scrapy/badge.svg?branch=master)](https://coveralls.io/github/dev-phoenix/hh_vcc_119170531__tst_scrapy?branch=master)
![GitHub repo size](https://img.shields.io/github/repo-size/dev-phoenix/hh_vcc_119170531__tst_scrapy)
<a href="https://github.com/dev-phoenix/hh_vcc_119170531__tst_scrapy/pulse" alt="Activity">
<img src="https://img.shields.io/github/commit-activity/m/dev-phoenix/hh_vcc_119170531__tst_scrapy" /></a>

[Scrapy docs](https://www.scrapy.org/)

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

### city choice:
```sh
# to choce city (default: Краснодар)
scrapy crawl alco -O result.json -a city=Москва
```

### run with proxy:
```sh
# collect proxy from ://proxy5.net
scrapy crawl alco -O proxy.json -a scenario=proxy

# run crawler with collected proxy
scrapy crawl alco -O result.json -a proxy_on=on
```

### set limit of collected proxy:
```sh
# collect proxy with chiced count (default: 1000)
scrapy crawl alco -O proxy.json -a scenario=proxy proxy_count=10
```

### run with filtered proxy:
```sh
# check live proxy for https. from proxy.json to proxy_filtered_3.json
python3 proxy_checker.py

# run crawler with filtered proxy
scrapy crawl alco -O result.json -a proxy_on=on proxy_from=proxy_filtered_3.json
```

### be carefully by loading unknown files !!!