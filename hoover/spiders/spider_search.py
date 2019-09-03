# -*- coding: utf-8 -*-
import scrapy


class SpiderSearch(scrapy.Spider):
    name = 'spider_search'
    # allowed_domains = ['hoover.org']
    start_urls = ['http://hoover.org/']
    basic_url = 'https://www.hoover.org'
    page_count = 0

    def start_requests(self):
        pass

    def parse(self, response):
        pass
