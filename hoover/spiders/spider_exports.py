# -*- coding: utf-8 -*-
import re

import scrapy

from hoover.config import parsing_rules
from hoover.items import ExpertItem, AbandonItem


class ExportsSpider(scrapy.Spider):
    name = 'spider_exports'
    allowed_domains = ['hoover.org']
    start_urls = ['https://www.hoover.org/fellows']

    def parse(self, response):
        urls = response.xpath(
            "//div[@id='main']//div[@class='view-content']//div[@class='fellows-row']//h3[contains(@class,'field-name-title')]/a/@href").extract()
        for url in urls:
            yield scrapy.Request(url=response.urljoin(url), callback=self.parse_expert)

    def _get_experts_data(self, category, parsing_rule_dict, response):
        name = response.xpath(parsing_rule_dict.get("name")).extract_first()
        head_portrait = response.xpath(parsing_rule_dict.get("head_portrait")).extract_first()
        jobs = response.xpath(parsing_rule_dict.get("job")).extract()
        job = ';'.join(jobs)
        research_field = response.xpath(parsing_rule_dict.get("research_field")).extract()
        research_field = ';'.join(research_field)
        brief_introd = response.xpath(parsing_rule_dict.get("brief_introd")).extract_first()
        rewards = response.xpath(parsing_rule_dict.get("reward"))


        data = {
            "name": name,
            "head_portrait": head_portrait,
            "job": job,
            "reward": reward,
            "research_field": research_field,
            "brief_introd": brief_introd,
        }
        return data

    def parse_expert(self, response):
        external_url = response.headers.get("Location")
        if external_url:
            external_url = external_url.decode()
        category = re.search('.*?hoover.org/(.*?)/\S+', response.url)
        if category:
            category = category.group(1)
            if category == "experts":
                parsing_rule_dict = parsing_rules.get(category)
                data = self._get_experts_data(category, parsing_rule_dict, response)
                item = ExpertItem(**data)
                yield item
            else:
                data = {"status_code": response.status, "internal_url": response.url, "external_url": external_url}
                item = AbandonItem(**data)
                yield item
        else:
            data = {"status_code": response.status, "internal_url": response.url, "external_url": external_url}
            item = AbandonItem(**data)
            yield item
