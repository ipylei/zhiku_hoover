# -*- coding: utf-8 -*-

parsing_rule_experts = {
    "name": "//div[@id='main']//div[contains(@class,'pane-node-title')]//h1/text()",
    "head_portrait": "//div[@id='main']//div[contains(@class,'field-name-field-fellow-img')]//img/@src",
    "job": "//div[@id='main']//div[contains(@class,'pane-node-field-fellow-position')]//div[@class='field-items']/div[@class='field-item even']/text()",
    "reward": "//div[@id='main']//div[@class='field-award-info']",
    "research_field": "//div[@id='main']//div[@class='field-name-field-tref-expertise']//div[@class='field-items']//div[@class='field-item']/a/text()",
    "brief_introd": "//div[@id='main']//div[contains(@class,'pane-node-body')]",
    "research_team": "//div[@id='main']//div[contains(@class,'field-name-field-fellow-teams')]//*[contains(@class,'field-name-field-ref-group')]//text()",
    "active_media": "//div[@id='main']//div[contains(@class,'field-name-field-fellow-sites')]//a/@href"
}
parsing_rule_news = {
    "title": "//meta[@property='og:title']/@content | //h1[@class='page-title']/text()",
    "publish_time": "//header[@class='article-header']//span[@class='date-display-single']/text()",
    "content": "//div[contains(@class,'field-name-body')]",
    "description": "//meta[@property='og:description']/@content | //meta[@name='description']/@content",
    "author": "//header[@class='article-header']//span[@class='field-items']/a/text()"
}
parsing_rule_events = parsing_rule_news
parsing_rule_research = parsing_rule_news

parsing_rules = {
    "profiles": parsing_rule_experts,
    "events": parsing_rule_events
}
