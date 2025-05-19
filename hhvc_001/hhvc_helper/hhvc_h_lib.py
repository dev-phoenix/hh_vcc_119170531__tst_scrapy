# hhvc_h_lib.py
"""helper for spiders"""
import urllib.parse as up


from hhvc_001.spiders.params import (
    CITY_UUID_DEF,
)

class HHVCSSHelper:
    """HH Vacancy Scrapy Spider Helper"""
    city_uuid = CITY_UUID_DEF

    def is_dict(self, obj):
        """check is the objecs instance of dictionary"""
        return obj.__class__.__name__ == "dict"

    def is_list(self, obj):
        """check is the objecs instance of array"""
        return obj.__class__.__name__ == "list"

    def is_str(self, obj):
        """check is the objecs instance of string"""
        return obj.__class__.__name__ == "str"

    def logp(self, *args, **kwargs):
        """colored print"""
        fg = kwargs.get("fg", 30)
        bg = kwargs.get("bg", 47)
        if "fg" in kwargs:
            del kwargs["fg"]
        if "bg" in kwargs:
            del kwargs["bg"]
        print()
        print(f"\033[1;{fg};1;{bg}m", end="")
        print(*args, **kwargs, end="\033[0m\n")

    def attrdump(self):
        """output self class attributes"""
        properties = [p for p in dir(self) if not p.startswith("_")]
        for p in properties:
            data = getattr(self, p)
            if not callable(data):
                print(f"properties: {p:>20} = {data}")

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
