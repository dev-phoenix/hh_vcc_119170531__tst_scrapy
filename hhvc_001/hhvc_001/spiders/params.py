# params.py
"""containing started prarameters for spider run"""

# set location
CITY_SET = "Москва"
CITY_SET = "Краснодар"

# default location
CITY_DEF = "Краснодар"
CITY_UUID_DEF = "4a70f9e0-46ae-11e7-83ff-00155d026416"

# template for collecting locations
CITIES_URL = "https://alkoteka.com/web-api/v1/city?page={page}"


# not work, needed new catalog parser
# "https://alkoteka.com/promotion/ot-2-kh-cena-nizhe-0525",

# array with catalog urls
START_URLS = [
    # "https://alkoteka.com/catalog/aksessuary-2"
    # "https://alkoteka.com/catalog/aksessuary-2/options-categories_bokaly-i-aksessuary-dlya-napitkov",
    # "https://alkoteka.com/catalog/skidki",
#     "https://alkoteka.com/catalog/slaboalkogolnye-napitki-2",
#     "https://alkoteka.com/catalog/slaboalkogolnye-napitki-2/\
# options-vid_pivo-temnoe-filtrovannoe/\
# options-vid_pivo-temnoe-nefiltrovannoe",
#     "https://alkoteka.com/catalog/slaboalkogolnye-napitki-2/\
# options-cena_400/options-cena_2990",
]
