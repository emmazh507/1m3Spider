# -*- coding: utf-8 -*-

__author__ = 'emma'

from scrapy.cmdline import execute

import sys
import os

print(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#execute(['scrapy','crawl','onem3spider'])
#execute(['scrapy','crawl','mj_spider'])
execute(['scrapy','crawl','gd_spider'])

# import scrapy
# from scrapy.crawler import CrawlerProcess
# from spiders.onem3spider import MJSpider
# from spiders.gd_spider import GdSpiderSpider
# from twisted.internet import reactor, defer
# from scrapy.crawler import CrawlerRunner
# from scrapy.utils.log import configure_logging
#
# configure_logging()
# runner = CrawlerRunner()
#
# @defer.inlineCallbacks
# def crawl():
#     yield runner.crawl(MJSpider)
#     yield runner.crawl(GdSpiderSpider)
#     reactor.stop()
#
# crawl()
# reactor.run() # the script will block here until the last crawl call is finished
