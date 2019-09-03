# -*- coding: utf-8 -*-

parsing_rule_experts = {
    "name": "//div[@id='main']//div[contains(@class,'pane-node-title')]//h1/text()",
    "head_portrait": "//div[@id='main']//div[contains(@class,'field-name-field-fellow-img')]//img/@src",
    "job": "//div[@id='main']//div[contains(@class,'pane-node-field-fellow-position')]//div[@class='field-items']/div[@class='field-item even']/text()",
    "reward": "//div[@id='main']//div[@class='field-award-info']/a",
    # todo 先不提出来，遍历每个Selector,调用reword.xpath(string("//a"))
    "research_field": "//div[@id='main']//div[@class='field-name-field-tref-expertise']//div[@class='field-items']//div[@class='field-item']/a/text()",
    "brief_introd": "//div[@id='main']//div[contains(@class,'pane-node-body')]",
}
parsing_rule_research = {}

parsing_rules = {
    "profiles": parsing_rule_experts
}
