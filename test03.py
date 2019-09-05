# -*- coding: utf-8 -*-
from newspaper import Article

# url = 'https://www.nationalreview.com/corner/journalism-donald-trump-conservative-media-revolution/'
url = 'https://www.worldaffairs.org/events/event/1876'
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
print('标题:', article.title)
print('时间:', article.publish_date)
print('正文:', article.text)
print('摘要:', article.summary)
print('作者:', article.authors)

print('配图:', article.top_image)
print('视频:', article.movies)
