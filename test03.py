# -*- coding: utf-8 -*-
from newspaper import Article

url = 'https://www.nationalreview.com/corner/journalism-donald-trump-conservative-media-revolution/'
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
