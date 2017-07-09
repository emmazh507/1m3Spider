# -*- coding: utf-8 -*-

__author__ = 'emma'

from scrapy.cmdline import execute

import sys
import os

print(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(['scrapy','crawl','mj_spider'])
#execute(['scrapy','crawl','onem3spider'])