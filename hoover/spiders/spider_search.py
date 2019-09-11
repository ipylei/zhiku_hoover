# -*- coding: utf-8 -*-
import datetime
import json
import re

import scrapy
from newspaper import Article

from hoover.config import parsing_rules
from hoover.items import SearchItem, ExpertItem, ExpertContactItem, AbandonItem
from hoover.settings import WEBSITE


class SearchSpider(scrapy.Spider):
    name = 'spider_search'
    # allowed_domains = ['hoover.org']
    # start_urls = ['http://hoover.org/']
    page_count = 0
    basic_url = 'https://www.hoover.org/site-search?keyword=news&src=navbar'

    def __init__(self, name=None, **kwargs):
        super(SearchSpider, self).__init__(name, **kwargs)
        self.keyword = kwargs.get('keyword') if kwargs.get('keyword') else 'news'
        self.page_size = kwargs.get('page_size') if kwargs.get('page_size') else 10

    def start_requests(self):
        start_url = self.basic_url.format(self.keyword)
        yield scrapy.Request(url=start_url)

    def parse(self, response):
        self.page_count += 1
        if self.page_count <= self.page_size:
            item_links = response.xpath(
                "//div[contains(@class,'view-search')]//div[@class='view-content']//h2/a/@href").extract()
            published_times = response.xpath(
                "//div[contains(@class,'view-search')]//div[@class='view-content']//div[@class='search-meta'][last()]/text()").extract()
            for i in range(len(item_links)):
                publish_time = published_times[i]
                yield scrapy.Request(url=response.urljoin(item_links[i]), callback=self.parse_detail,
                                     meta={'dont_redirect': False, 'handle_httpstatus_list': [301, 302],
                                           "publish_time": publish_time
                                           })

            next_url = response.xpath("//li[@class='pager-next']/a/@href").extract_first()
            if next_url:
                yield scrapy.Request(url=response.urljoin(next_url))

    @staticmethod
    def _get_item_data(category, parsing_rule_dict, response):
        title = response.xpath(parsing_rule_dict.get("title")).extract_first()
        published_time = response.xpath(parsing_rule_dict.get("publish_time")).extract_first()
        publish_time = str(datetime.datetime.strptime(published_time, "%A, %B %d, %Y"))
        content = response.xpath(parsing_rule_dict.get("content")).extract_first()
        description = response.xpath(parsing_rule_dict.get("description")).extract_first()
        data = {
            "Url": response.url,
            "Title": title,
            "Author": "",
            "PublishTime": publish_time,
            "Keywords": "",
            "Abstract": description if description else "",
            "Content": content if content else "",
            "Category": category,
            "topic": "",
            "tags": "",
            "site_name": WEBSITE
        }
        return data

    @staticmethod
    def _get_experts_data(parsing_rule_dict, response):
        name = response.xpath(parsing_rule_dict.get("name")).extract_first()
        head_portrait = response.xpath(parsing_rule_dict.get("head_portrait")).extract_first()
        jobs = response.xpath(parsing_rule_dict.get("job")).extract()
        job = ','.join(jobs)
        research_field = response.xpath(parsing_rule_dict.get("research_field")).extract()
        research_field = ','.join(research_field)
        brief_introd = response.xpath(parsing_rule_dict.get("brief_introd")).extract_first()
        rewards_selector = response.xpath(parsing_rule_dict.get("reward"))
        reward = rewards_selector.xpath("string(.)").extract()
        reward = ','.join(reward)
        # 研究团队
        # research_team = response.xpath(parsing_rule_dict.get("research_team")).extract()
        # research_team = ','.join(research_team)
        data = {
            "name": name,
            "experts_url": response.url,
            "img_url": head_portrait if head_portrait else "",
            "abstract": brief_introd if brief_introd else "",
            "research_field": research_field if research_field else "",
            "job": job if job else "",
            "education": "",

            "reward": reward if reward else "",
            # "research_team": research_team,
            "relevant": "",
            # "createTime": ""
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
            # active_media = json.dumps(active_media_dict, ensure_ascii=False)
            active_media = ','.join(active_media_dict.values())
        else:
            active_media = ""

        contact = contact if contact else ""
        data.update({"contact": contact, "active_media": active_media})
        return data

    @staticmethod
    def newspaper_parse(url, status_code, publish_time):
        article = Article(url)
        # 下载网页
        article.download()
        # 网页解析
        article.parse()

        data = dict()
        data['Url'] = url
        data['Title'] = article.title if article.title else ""
        data['Author'] = ""
        data['PublishTime'] = publish_time
        data['Keywords'] = ",".join(article.keywords)
        data['Abstract'] = ""
        data['Content'] = article.text if article.text else ""
        data['Category'] = ""
        data['topic'] = ""
        data['tags'] = ""
        data['site_name'] = WEBSITE
        # data['method'] = 'newspaper'
        # data['status_code'] = status_code
        return data

    def parse_detail(self, response):
        publish_time = response.meta.get("publish_time")
        if publish_time:
            publish_time = publish_time.strip()
            publish_time = str(datetime.datetime.strptime(publish_time, "%A, %B %d, %Y"))
        else:
            publish_time = ""

        # 重定向的网址
        external_url = response.headers.get("Location")
        if external_url:
            external_url = external_url.decode()
        if response.status in [301, 302] and external_url:
            data = self.newspaper_parse(external_url, response.status, publish_time)
            item = SearchItem(**data)
            yield item

        elif response.status == 200:
            category = re.search('.*?hoover.org/(.*?)/\S+', response.url)
            if category:
                category = category.group(1)
                parsing_rule_dict = parsing_rules.get(category)
                if category in parsing_rules and category != "profiles":
                    data = self._get_item_data(category, parsing_rule_dict, response)
                    item = SearchItem(**data)
                    yield item
                elif category in parsing_rules and category == "profiles":
                    data = self._get_experts_data(parsing_rule_dict, response)
                    # contacts = data.pop("contact")
                    item = ExpertItem(**data)
                    yield item
                    # for key, value in contacts.items():
                    #     contact_data = {"url": response.url, "name": data.get("name"), "type": key, "contact": value}
                    #     item2 = ExpertContactItem(**contact_data)
                    #     yield item2  # 联系方式
                else:
                    data = self.newspaper_parse(response.url, response.status, publish_time)
                    item = SearchItem(**data)
                    yield item
            else:
                data = self.newspaper_parse(response.url, response.status, publish_time)
                item = SearchItem(**data)
                yield item
        # else:  # 其他响应码
        #     data = {"status_code": response.status, "internal_url": response.url, "external_url": external_url}
        #     item = AbandonItem(**data)
        #     yield item
