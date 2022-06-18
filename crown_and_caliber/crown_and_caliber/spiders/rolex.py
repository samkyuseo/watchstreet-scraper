import scrapy
from datetime import datetime


class RolexSpider(scrapy.Spider):
    name = "rolex"
    start_urls = [f"https://www.crownandcaliber.com/collections/rolex-watches"]
    user_agent = "Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0"
    page = 100  # some arbitrary big amount

    def parse(self, response):
        for i in range(1, self.page):
            yield response.follow(
                f"https://www.crownandcaliber.com/collections/rolex-watches?page={i}",
                callback=self.parse_page,
            )

    def parse_page(self, response):
        links = response.css("a.grid-view-item__link::attr(href)").getall()
        # Scrape all watch page links and crawl
        for link in links:
            yield response.follow(
                f"https://www.crownandcaliber.com{link}", callback=self.parse_watch
            )

    def parse_watch(self, response):
        has_nickname = len(response.css("span.main-product-name::text").getall()) == 2
        prod_specs = response.css("div.prod-specs > div")
        specs = {}
        for ps in prod_specs:
            key = ps.css("span::text").get()
            value = ps.css("span.list-value::text").get()
            if key and value:
                snake_case_key = (
                    key.strip().replace("-", "").strip().replace(" ", "_").lower()
                )
                value = value.strip().replace("\n        ", "")
                if value == "Yes" or value == "No":
                    value = True if value == "Yes" else False
                specs[snake_case_key] = value
        yield {
            "brand": response.css("span.vendor::text").get().strip(),
            "price": response.css("span.current-price::text").get().strip(),
            "model": response.css("span.main-product-name::text").get().strip(),
            "nickname": None
            if not has_nickname
            else response.css("span.main-product-name::text").getall()[1].strip(),
            "reference": response.css("span.model-number::text").get().strip(),
            "url": response.request.url,
            "date": datetime.today().strftime("%Y-%m-%d"),
            **specs,
        }
