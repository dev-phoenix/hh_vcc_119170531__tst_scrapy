# test project for parser with scrapy
## hh vacancy 119170531 -- test scrapy parser

[Scrapy docs](https://www.scrapy.org/)

### to start:
```sh
git clone https://github.com/dev-phoenix/hh_vcc_119170531__tst_scrapy.git
cd hh_vcc_119170531__tst_scrapy/
pip -m venv .env
. ./.env/bin/activate
# pip install wheel
pip install -r requirements.txt

# then check contents or run for test
python main.py
# or run with scrapy command
# scrapy crawl spider_name -O result.json
cd hhvc_001
scrapy list
scrapy crawl quotes -O result.json
```

## be carefully by loading unknown files !!!