# models.py
"""template variables"""

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
