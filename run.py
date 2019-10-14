# -*- coding: utf-8 -*-

from scrapy import cmdline

# cmdline.execute('scrapy crawl spider_exports -o result.json'.split())

cmdline.execute('scrapy crawl spider_export'.split())
# cmdline.execute('scrapy crawl spider_search'.split())
