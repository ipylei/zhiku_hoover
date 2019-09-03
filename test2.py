# -*- coding: utf-8 -*-

# active_media = []
# keys = ['a', 'b', 'c']
# values = [1, 2, 3]
# active_media_dict = dict(zip(keys, values))
# for key, value in active_media_dict.items():
#     active_media.append('{}:{}'.format(key, value))
#
# active_media = ';'.join(active_media)
# print(active_media)


import json

with open('result.json', 'r')as f:
    contents = json.load(f)
    for content in contents:
        if content.get("active_media"):
            print(content['url'], '----', content["active_media"])
