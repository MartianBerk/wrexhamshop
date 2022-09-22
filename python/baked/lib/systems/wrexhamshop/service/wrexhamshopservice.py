from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from typing import Dict


class WrexhamShopService:

    _URL = "https://shop.wrexhamafc.co.uk"
    _PRODUCT_EXT = "product"

    def __init__(self, config: Dict):
        self._config = config
        self._connection = None

    def _open_connection(self):
        if not self._connection:
            options = Options()
            options.add_argument("--headless")
            self._connection = Chrome(options=options)

    def find_product(self, product):
        self._open_connection()

        if product not in self._config["products"]:
            raise ValueError(f"Product '{product}' is unknown.")

        try:
            product_config = self._config["products"][product]
            url_ext = product_config["url_ext"]
            outer_div_class = product_config["outer_div_class"]
            inner_div_class = product_config["inner_div_class"]
            price_class = product_config["price_class"]
            stock_class = product_config["stock_class"]

            url = "/".join([self._URL, self._PRODUCT_EXT, url_ext])
            self._connection.get(url)
            html = self._connection.page_source
            content = BeautifulSoup(html, "lxml")

            product_div = content.find("div", attrs={"class": [outer_div_class]})
            if not product_div:
                raise ValueError(f"Product '{product}' not found using class '{outer_div_class}'.")

            product_content_div = product_div.find("div", attrs={"class": [inner_div_class]})
            if not product_content_div:
                raise ValueError(f"Product data for '{product}' not found using class '{inner_div_class}'.")

            price = product_content_div.find("p", attrs={"class": [price_class]})
            stock = product_content_div.find("p", attrs={"class": [stock_class]})
            if not price or not stock:
                raise ValueError(f"Stock and price information not found for product '{product}' in '{inner_div_class}'.")

            return (price.text, stock.text,)

        except KeyError as e:
            raise ValueError(f"Invalid product config: cannot find attribute '{str(e)}'")


if __name__ == "__main__":
    import json
    
    with open("config/wrexhamshop/products.json", "r") as fh:
        service = WrexhamShopService(json.load(fh))

    service.find_product("snapbackcap")
