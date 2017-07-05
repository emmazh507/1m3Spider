# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class Onem3spiderAllSpider(CrawlSpider):
    name = 'onem3spider'
    allowed_domains = ['www.1point3acres.com']
    start_urls = ['http://www.1point3acres.com/bbs/']

    rules = (
 	    Rule(LinkExtractor(allow=("forum-145-1.html", "forum-28-1.html"), ), follow=True),
        #???any better way to deal with next_page???
        Rule(LinkExtractor(allow=(".*fid=145.*", ".*fid=28.*"), ), follow=True),
        Rule(LinkExtractor(allow=('thread.*'), restrict_xpaths=('//table[@summary="forum_145"]', '//table[@summary="forum_28"]', '//span[@id="fd_page_top"]')), callback='parse_item',),
    )

    def parse_item(self, response):
        i = {}
        print(response.css("span#thread_subject::text"))
        #i['domain_id'] = response.xpath('//input[@id="sid"]/@value').extract()
        #i['name'] = response.xpath('//div[@id="name"]').extract()
        #i['description'] = response.xpath('//div[@id="description"]').extract()
        return i
