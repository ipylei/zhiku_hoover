# -*- coding: utf-8 -*-
import json
import re

import scrapy

from hoover.config import parsing_rules, parsing_rule_experts
from hoover.items import ExpertItem, AbandonItem, ExpertContactItem


class ExportsSpider(scrapy.Spider):
    name = 'spider_exports'
    # allowed_domains = ['hoover.org']
    start_urls = ['https://www.hoover.org/fellows']

    def parse(self, response):
        urls = response.xpath(
            "//div[@id='main']//div[@class='view-content']//h3[contains(@class,'field-name-title')]/a/@href").extract()
        for url in urls:
            yield scrapy.Request(url=response.urljoin(url), callback=self.parse_expert)

    def _get_experts_data(self, parsing_rule_dict, response):
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
        # 研究团队
        research_team = response.xpath(parsing_rule_dict.get("research_team")).extract()
        research_team = ';'.join(research_team)
        data = {
            "url": response.url,
            "name": name,
            "head_portrait": head_portrait,
            "job": job,
            "reward": reward,
            "research_field": research_field,
            "brief_introd": brief_introd,
            "research_team": research_team,
        }

        # 联系方式
        contact = dict()
        # 活跃的媒体
        active_media_dict = dict()
        active_medias = response.xpath(parsing_rule_dict.get("active_media")).extract()
        for media in active_medias:
            if 'twitter' in media:
                active_media_dict['twitter'] = media
        if active_media_dict:
            contact.update(active_media_dict)  # 更新联系方式，添加活跃的媒体
            active_media = json.dumps(active_media_dict, ensure_ascii=False)
        else:
            active_media = ''
        data.update({"contact": contact, "active_media": active_media})
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
                data = self._get_experts_data(parsing_rule_dict, response)
                contacts = data.pop("contact")
                item = ExpertItem(**data)
                for key, value in contacts.items():
                    contact_data = {"url": response.url, "name": data.get("name"), "type": key, "contact": value}
                    item2 = ExpertContactItem(**contact_data)
                    yield item2  # 联系方式
                yield item
            else:
                data = {"status_code": response.status, "internal_url": response.url, "external_url": external_url}
                item = AbandonItem(**data)
                yield item
        else:
            data = {"status_code": response.status, "internal_url": response.url, "external_url": external_url}
            item = AbandonItem(**data)
            yield item

        # url = response.url
        # active_media = response.xpath(parsing_rule_experts.get("active_media")).extract()
        # yield ExpertItem(url=url, active_media=active_media)
