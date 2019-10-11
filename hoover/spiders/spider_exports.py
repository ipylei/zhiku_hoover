# -*- coding: utf-8 -*-
import datetime
import json
import re

import scrapy
from newspaper import Article

from hoover.config import parsing_rules, parsing_rule_experts
from hoover.items import ExpertItem, AbandonItem, ExpertContactItem, SearchItem


class ExportsSpider(scrapy.Spider):
    name = 'spider_exports'
    # allowed_domains = ['hoover.org']
    start_urls = ['https://www.hoover.org/fellows']

    def __init__(self,
                 keyword='china',
                 page_size=10,
                 # mq_host='10.4.9.177',
                 mq_host='39.98.176.208',
                 mq_username='admin',
                 mq_password='123456',
                 # mq_host='127.0.0.1',
                 # mq_username='guest',
                 # mq_password='guest',

                 mq_port=5672, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyword = keyword
        self.page_size = int(page_size)
        self.mq_host = mq_host
        self.mq_port = int(mq_port)
        self.mq_username = mq_username
        self.mq_password = mq_password

    def parse(self, response):
        urls = response.xpath(
            "//div[@id='main']//div[@class='view-content']//h3[contains(@class,'field-name-title')]/a/@href").extract()
        for url in urls:
            yield scrapy.Request(url=response.urljoin(url), callback=self.parse_expert)

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
            "img_url": response.urljoin(head_portrait) if head_portrait else "",
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

        contact = [contact] if contact else ""
        data.update({"contact": contact, "active_media": active_media})
        return data

    def parse_expert(self, response):
        # external_url = response.headers.get("Location")
        # if external_url:
        #     external_url = external_url.decode()
        category = re.search('.*?hoover.org/(.*?)/\S+', response.url)
        if category:
            category = category.group(1)
            if category == "profiles":
                parsing_rule_dict = parsing_rules.get(category)
                data = self._get_experts_data(parsing_rule_dict, response)
                # contacts = data.pop("contact")
                item = ExpertItem(**data)
                yield item

            # todo 采集专家发布的文章
            # self._parse_article_url(response)
            item_selectors = response.xpath(
                "//div[@id='mini-panel-fellow_research']//div[@class='view-content']/div[contains(@class,'views-row')]")
            for selector in item_selectors:
                url = selector.xpath(".//h2/a/@href").extract_first()
                # publish_time = selector.xpath(".//span[@class='date-display-single']/text()").extract_first()
                if url:
                    yield scrapy.Request(url=response.urljoin(url), callback=self.parse_detail,
                                         meta={'dont_redirect': False, 'handle_httpstatus_list': [301, 302],
                                               # "publish_time": publish_time,
                                               'data_source': 5})
            # 提取出下一页的url
            next_url = response.xpath("//a[contains(text(),'next')]/@href").extract_first()
            if next_url:
                yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_article_url)

    def parse_article_url(self, response):
        # 采集专家发布的文章
        item_selectors = response.xpath(
            "//div[@id='mini-panel-fellow_research']//div[@class='view-content']/div[contains(@class,'views-row')]")
        for selector in item_selectors:
            url = selector.xpath(".//h2/a/@href").extract_first()
            # publish_time = selector.xpath(".//span[@class='date-display-single']/text()").extract_first()
            if url:
                yield scrapy.Request(url=response.urljoin(url), callback=self.parse_detail,
                                     meta={'dont_redirect': False, 'handle_httpstatus_list': [301, 302],
                                           # "publish_time": publish_time,
                                           'data_source': 5})
        # 提取出下一页的url
        next_url = response.xpath("//a[contains(text(),'next')]/@href").extract_first()
        if next_url:
            yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_article_url)

    @staticmethod
    def _get_item_data(category, parsing_rule_dict, response):
        title = response.xpath(parsing_rule_dict.get("title")).extract_first()
        published_time = response.xpath(parsing_rule_dict.get("publish_time")).extract_first()
        publish_time = str(datetime.datetime.strptime(published_time, "%A, %B %d, %Y"))
        content = response.xpath(parsing_rule_dict.get("content")).extract_first()
        description = response.xpath(parsing_rule_dict.get("description")).extract_first()
        xpath_author = parsing_rule_dict.get("author")
        if xpath_author:
            author = response.xpath(xpath_author).extract()
            author = ','.join(author)
        else:
            author = ""
        data = {
            "Url": response.url,
            "Title": title,
            "Author": author,
            "PublishTime": publish_time,
            "Keywords": "",
            "Abstract": description if description else "",
            "Content": content if content else "",
            "Category": category,
            "topic": "",
            "tags": "",
            # "site_name": WEBSITE
        }
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
        # data['site_name'] = WEBSITE
        # data['method'] = 'newspaper'
        # data['status_code'] = status_code
        return data

    def parse_detail(self, response):
        data_source = response.meta.get('data_source')

        # publish_time = response.meta.get("publish_time")
        # if publish_time:
        #     publish_time = publish_time.strip()
        #     publish_time = str(datetime.datetime.strptime(publish_time, "%A, %B %d, %Y"))
        # else:
        #     publish_time = ""
        #
        # # 重定向的网址
        # external_url = response.headers.get("Location")
        # if external_url:
        #     external_url = external_url.decode()
        # if response.status in [301, 302] and external_url:
        #     data = self.newspaper_parse(external_url, response.status, publish_time)
        #     data["DataSource"] = data_source
        #     item = SearchItem(**data)
        #     yield item

        if response.status == 200:
            category = re.search('.*?hoover.org/(.*?)/\S+', response.url)
            if category:
                category = category.group(1)
                parsing_rule_dict = parsing_rules.get(category)
                if category in parsing_rules and category != "profiles":
                    data = self._get_item_data(category, parsing_rule_dict, response)
                    data["DataSource"] = data_source
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
        #         else:
        #             data = self.newspaper_parse(response.url, response.status, publish_time)
        #             data["DataSource"] = data_source
        #             item = SearchItem(**data)
        #             yield item
        #     else:
        #         data = self.newspaper_parse(response.url, response.status, publish_time)
        #         data["DataSource"] = data_source
        #         item = SearchItem(**data)
        #         yield item
        # # else:  # 其他响应码
        # #     data = {"status_code": response.status, "internal_url": response.url, "external_url": external_url}
        # #     item = AbandonItem(**data)
        # #     yield item
