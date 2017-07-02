# -*- coding: utf-8 -*-
import scrapy
import requests
import re
from bs4 import BeautifulSoup
from ..items import MJItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule



# []-->list() {}-->dict()
class onem3point(scrapy.Spider):
    # 注释-必须字段，爬虫名，scrapy list命令行会列出name
    name = 'mj_spider'
    # 注释-必须字段，允许的爬取的url域名，如果url中域名不是这段不进行爬取。这里是python的列表类型，可以放多个链接
    allowed_domain = ["www.1point3acres.com"]
    # 注释-必须字段，爬虫启动时首先打开的url。这里是python的列表类型，可以放多个链接
    start_urls = ['http://www.1point3acres.com/bbs/forum-145-1.html']
    def parse(self, response):
        print("test")

    def parse_info(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        mj_info = response.meta['mj_info']
        mj_info['title'] = soup.find('span', {'id': 'thread_subject'}).get_text()
        postlist = soup.find('div', {'id': 'postlist'})
        #     postlist = postlist.find_all('div', {'id':re.compile(r"post_.*")})
        tag = 'test'
        tags = postlist.find('div', {'class': 'pcb'}).find('u').find_all('b')
        mj_info['tag'] = tags[3].get_text()
        postlist = postlist.find_all('td', {'class': 't_f'})
        mj_info['context'] = postlist[0].get_text()
        return mj_info

    def parse_link(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        threads = soup.find('table', {'summary': 'forum_145'}).find_all('tbody')
        print(len(threads))
        for thread in threads:
            if thread.get('id').find('normalthread') == -1:
                continue
            mj_info = MJItem()
            link = thread.find('th', {'class': 'common'}).find('a', {"class": 's', 'class': 'xst'}).get('href')
            yield scrapy.Request(link, meta={'mj_info': mj_info}, callback=self.parse_info)



    def parse(self, response):
        url = 'http://www.1point3acres.com/bbs/forum.php?mod=forumdisplay&fid=145&sortid=311&%1=&sortid=311&page={}'
        soup = BeautifulSoup(response.text, 'lxml')
        pages = soup.find('span', {'id': 'fd_page_bottom'}).find_all('a')
        total = 0
        for page in pages:
            try:
                page = int(re.sub('\D', '', page.get_text()))
            except:
                page = 0
            if page > total:
                total = page
        print(total)

        for i in range(1, 2):
            # response.url是当前response的请求路径，拼接数字加上后面的一个字符串，就得到了需要的链接
            yield scrapy.Request(url.format(i), callback=self.parse_link)