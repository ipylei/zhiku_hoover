# -*- coding: utf-8 -*-


import datetime

# string = "Thursday, August 29, 2019"
string = "Thursday, May 2, 2019"
res = datetime.datetime.strptime(string, "%A, %B %d, %Y")
print(res, type(res))
