# -*- coding: utf-8 -*-
import re

import scrapy

from hoover.config import parsing_rules
from hoover.items import ExpertItem, AbandonItem


class ExportsSpider(scrapy.Spider):
    name = 'spider_exports'
    # allowed_domains = ['hoover.org']
    start_urls = ['https://www.hoover.org/fellows']

    def parse(self, response):
        urls = response.xpath(
            "//div[@id='main']//div[@class='view-content']//h3[contains(@class,'field-name-title')]/a/@href").extract()
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
        rewards_selector = response.xpath(parsing_rule_dict.get("reward"))
        reward = rewards_selector.xpath("string(.)").extract()
        reward = ';'.join(reward)
        research_team = response.xpath(parsing_rule_dict.get("research_team")).extract()
        research_team = ';'.join(research_team)
        data = {
            "url": response.url,
            "category": category,
            "name": name,
            "head_portrait": head_portrait,
            "job": job,
            "reward": reward,
            "research_field": research_field,
            "brief_introd": brief_introd,
            "research_team": research_team,
        }
        active_media_selector = response.xpath(parsing_rule_dict.get("active_media"))
        if active_media_selector:
            keys = active_media_selector.xpath("./text()").extract()
            values = active_media_selector.xpath("./@href").extract()
            active_media = []
            active_media_dict = dict(zip(keys, values))
            for key, value in active_media_dict.items():
                active_media.append('{}:{}'.format(key, value))
            active_media = ';'.join(active_media)
            data["active_media"] = active_media
        return data

    def parse_expert(self, response):
        external_url = response.headers.get("Location")
        if external_url:
            external_url = external_url.decode()
        category = re.search('.*?hoover.org/(.*?)/\S+', response.url)
        if category:
            category = category.group(1)
            if category == "profiles":
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
