# -*- coding: utf-8 -*-
import requests
import re
import scrapy
from ..items import MJItem
from bs4 import BeautifulSoup
from scrapy.loader import ItemLoader


class onem3point(scrapy.Spider):
     # 注释-必须字段，爬虫名，scrapy list命令行会列出name
     name = 'mj_spider'
     # 注释-必须字段，允许的爬取的url域名，如果url中域名不是这段不进行爬取。这里是python的列表类型，可以放多个链接
     allowed_domians = ['www.1point3acres.com']
     # 注释-必须字段，爬虫启动时首先打开的url。这里是python的列表类型，可以放多个链接# -*- coding: utf-8 -*-
     start_urls = ['http://www.1point3acres.com/bbs/forum-145-1.html']

     def parse_info(self,response):

         item_loader = ItemLoader(item=MJItem(), response=response)
         #postlist = response.css("div[id='postlist']")

        #:::tags的提取
        #tags = postlist.xpath("//div[@class='pcb']//u//b//text()").extract()[3] 注意/和//的用法，有的不是直接在第一层子类
        #postlist.xpath("//div[@class='pcb']//u//b[4]//text()")-->css对象（xpath内部数组从1开始计数）
        #tags = postlist.css("div[class='pcb'] u b font::text").extract() 注意要一起精确到font

         item_loader.add_value("url", response.url)
         item_loader.add_css("title", "span#thread_subject::text")
         item_loader.add_xpath("tags", "//div[@id='postlist']//div[@class='pcb']//u//b[4]//text()")
         item_loader.add_xpath("content", "//div[@id='postlist']//td[@class='t_f']//text()")

         mj_item = item_loader.load_item()
         yield mj_item


     def parse_link(self,response):
         soup = BeautifulSoup(response.text, 'lxml')
         threads = soup.find('table', {'summary':'forum_145'}).find_all('tbody')
         print(len(threads))      
         for thread in threads:
              mj_info = MJItem()
              if thread.get('id').find('normalthread')==-1:
                  continue
              link = thread.find('th',{'class':'common'}).find('a', {"class":'s','class':'xst'}).get('href')
              #yield scrapy.Request(link, meta={'mj_info':mj_info}, callback=self.parse_info)
              yield scrapy.Request(link, callback=self.parse_info)


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
