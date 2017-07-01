# -*- coding: utf-8 -*-
import requests
import re
import scrapy
from ..items import Onem3SpiderItem
from bs4 import BeautifulSoup


class onem3point(scrapy.Spider):
     # 注释-必须字段，爬虫名，scrapy list命令行会列出name
     name = 'mj_spider'
     # 注释-必须字段，允许的爬取的url域名，如果url中域名不是这段不进行爬取。这里是python的列表类型，可以放多个链接
     allowed_domians = ['http://www.1point3acres.com']
     # 注释-必须字段，爬虫启动时首先打开的url。这里是python的列表类型，可以放多个链接
     start_urls = ['http://www.1point3acres.com/bbs/forum-145-1.html']

     def parse_info(self,response):
         soup = BeautifulSoup(response.text, 'lxml')
         mj_info = response.meta['mj_info']

         postlist = soup.find('div', {'id':'postlist'})
         mj_info['title'] = soup.find('span', {'id':'thread_subject'}).get_text()
         tags = postlist.find('div',{'class':'pcb'}).find('u').find_all('b')
         mj_info['tag'] = tags[3].get_text()
         print(mj_info['tag'])
         postlist = postlist.find_all('td',{'class':'t_f'})
         mj_info['context'] = postlist[0].get_text()
         return mj_info

     def parse_link(self,response):
         soup = BeautifulSoup(response.text, 'lxml')
         threads = soup.find('table', {'summary':'forum_145'}).find_all('tbody')
         print(len(threads))      
         for thread in threads:
              mj_info = Onem3SpiderItem()
              if thread.get('id').find('normalthread')==-1:
                  continue
              link = thread.find('th',{'class':'common'}).find('a', {"class":'s','class':'xst'}).get('href')
              yield scrapy.Request(link, meta={'mj_info':mj_info}, callback=self.parse_info) 


     def parse(self,response):
         soup = BeautifulSoup(response.text, 'lxml')
         url = 'http://www.1point3acres.com/bbs/forum.php?mod=forumdisplay&fid=145&sortid=311&%1=&sortid=311&page={}'
   
         pages = soup.find('span', {'id':'fd_page_bottom'}).find_all('a')
     
         total = 0
         for page in pages:
               try:
                  page = int(re.sub('\D','',page.get_text()))
               except:
                  page = 0 
               if page > total:
                  total = page
         print(total)
   
         for i in range(1, 2):
               yield scrapy.Request(url.format(i), callback=self.parse_link) 
