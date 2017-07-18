# -*- coding: utf-8 -*-
import requests
import re
import scrapy
import datetime
from onem3_spider.items import MJItem
from scrapy.loader import ItemLoader


class MJSpider(scrapy.Spider):
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
         item_loader.add_value("post_date", response.meta.get("post_date"))
         item_loader.add_value("url", response.url)
         item_loader.add_css("title", "span#thread_subject::text")
         item_loader.add_xpath("tags", "//div[@id='postlist']//div[@class='pcb']//u//b[4]//text()")
         item_loader.add_xpath("content", "//div[@id='postlist']//td[@class='t_f']//text()")

         mj_item = item_loader.load_item()
         yield mj_item


     def parse_link(self,response):
         #soup = BeautifulSoup(response.text, 'lxml')
         #threads = soup.find('table', {'summary':'forum_145'}).find_all('tbody')
         threads = response.xpath("//table[@summary='forum_145']//tbody")
         print(len(threads))      
         for thread in threads:
              mj_info = MJItem()
              if thread.css("::attr(id)").extract_first("").find('normalthread')==-1:
                  continue
              #?????[class='new']
              link = thread.css("tr th[class='common'] a[class='s xst']::attr(href)").extract()[0]
              post_date = thread.css("td[class='by'] span::attr(title)").extract_first()
              if not post_date:
                  post_date = thread.css("td[class='by'] span::text").extract_first()
                  print("HELLO")
              post_date = re.match("(\d+[-]\d+[-]\d+).*", post_date).group(1)
              #if not re.sub("(.*(\d+[-]\d+[-]\d+).*)", "", post_date):
              #    post_date = datetime.datetime.strptime()

              #yield scrapy.Request(link, meta={'mj_info':mj_info}, callback=self.parse_info)
              yield scrapy.Request(link, meta={"post_date":post_date}, callback=self.parse_info)


     def parse(self,response):
         #soup = BeautifulSoup(response.text, 'lxml')
         url = 'http://www.1point3acres.com/bbs/forum.php?mod=forumdisplay&fid=145&sortid=311&%1=&sortid=311&page={}'

         pages = response.xpath("//span[@id='fd_page_bottom']//a/text()").extract()

         total = 0
         for page in pages:
               try:
                  page = int(re.sub('\D','',page))
               except:
                  page = 0
               if page > total:
                  total = page
         print(total)

         for i in range(1, total):
               yield scrapy.Request(url.format(i), callback=self.parse_link)
