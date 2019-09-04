# -*- coding: utf-8 -*-
from newspaper import Article

# url = "http://hd.stheadline.com/news/daily/hk/789947/%E6%97%A5%E5%A0%B1-%E6%B8%AF%E8%81%9E-%E8%90%BD%E9%96%98%E5%99%B4%E6%BB%85%E7%81%AB%E7%AD%92%E6%8B%92%E8%AD%A6-%E7%A4%BA%E5%A8%81%E8%80%85%E4%BD%94%E9%A0%98%E5%85%83%E6%9C%97%E7%AB%99"
# url = 'https://www.nationalreview.com/corner/journalism-donald-trump-conservative-media-revolution/'
# url = 'https://www.hoover.org/research/theres-good-news-and-theres-really-good-news'
url = 'https://www.hoover.org/news/notable-events-2018'

# 创建文章对象
article = Article(url)
# 下载网页
article.download()
# 网页解析
article.parse()
# # 打印html文档
# print(article.html)

# 关键词
print('关键词:{}'.format(article.keywords))

# 文章摘要
print('摘要:{}'.format(article.summary))

print('标题：' + article.title)
print('作者:{}'.format(article.authors))
print('时间:{}'.format(article.publish_date))
print('图片:{}'.format(article.top_image))
print('正文:' + article.text)
