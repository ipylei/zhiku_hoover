# -*- coding: utf-8 -*-
import datetime
import re

import scrapy

from hoover.config import parsing_rules
from hoover.settings import PAGE_COUNT


class SpiderSearch(scrapy.Spider):
    name = 'spider_search'
    # allowed_domains = ['hoover.org']
    # start_urls = ['http://hoover.org/']
    page_count = 0
    basic_url = 'https://www.hoover.org/site-search?keyword=news&src=navbar'

    def start_requests(self):
        search_words = 'events'
        start_url = self.basic_url.format(search_words)
        yield scrapy.Request(url=start_url)

    def parse(self, response):
        self.page_count += 1
        if self.page_count <= PAGE_COUNT:
            item_links = response.xpath(
                "//div[contains(@class,'view-search')]//div[@class='view-content']//h2/a/@href").extract()
            for url in item_links:
                yield scrapy.Request(url=url, callback=self.parse_detail)

    @staticmethod
    def _get_item_data(category, parsing_rule_dict, response):
        title = response.xpath(parsing_rule_dict.get("title")).extract_first()
        published_time = response.xpath(parsing_rule_dict.get("publish_time")).extract_first()
        publish_time = datetime.datetime.strptime(published_time, "%A, %B %d, %Y")
        content = response.xpath(parsing_rule_dict.get("content")).extract_first()
        description = response.xpath(parsing_rule_dict.get("description")).extract_first()
        data = {
            "category": category,
            "title": title,
            "publish_time": publish_time,
            "content": content,
            "description": description,
        }
        return data

    def parse_detail(self, response):
        category = re.search('.*?hoover.org/(.*?)/\S+', response.url)
        if category:
            category = category.group(1)
            parsing_rule_dict = parsing_rules.get("category")
            data = self._get_item_data(category, parsing_rule_dict, response)
            yield data
