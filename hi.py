import scrapy


class HiSpider(scrapy.Spider):
    name = 'hi'
    allowed_domains = ['google.com']
    start_urls = ['http://google.com/']

    def parse(self, response):
        pass
