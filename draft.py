# -*- coding: utf-8 -*-
import re

# url = "https://www.hoover.org/events/fouad-ajami-fellowship-annual-lecture-speaker-steve-hadley"
# url = "https://www.hoover.org/events/cardinal-conversations-francis-fukuyama-and-charles-murray-inequality-and-populism"

url = "https://www.hoover.org/research/july-2019-updates-directors-desk"
topic = re.search('.*?hoover.org/(.*?)/\S+', url)
if topic:
    topic = topic.group(1)
    print(topic)
else:
    print('----')
