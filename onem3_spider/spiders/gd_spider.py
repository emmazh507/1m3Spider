# -*- coding: utf-8 -*-
import scrapy
import requests
import re
import time
import pickle
import os.path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support.ui import Select
from items import GDItem
from scrapy.loader import ItemLoader


try:
    import urlparse as parse
except:
    from urllib import parse


class GdSpiderSpider(scrapy.Spider):
    name = 'gd_spider'
    allowed_domains = ['www.glassdoor.com']
    start_urls = ['http://www.glassdoor.com/']

    def parse(self, response):
        print(self.isLogin())
        if not self.isLogin():
            self.login()


        searchlist = ['huawei','apple','yahoo','google','facebook','linkedin', 'twitter', 'amazon']
        urllist = []
        tarlist=['Interview']
        browser = webdriver.PhantomJS("/Users/emmazhuang/Documents/Python/phantomjs-2.1.1-macosx/bin/phantomjs")
        #browser = webdriver.Chrome(executable_path="/Users/emmazhuang/Documents/Python/chromedriver")

        browser.get("https://www.glassdoor.com/"+tarlist[0]+"/index.htm")

        print(browser.current_url)
        cookies = pickle.load(open("cookies.pkl", "rb"))
        for cookie in cookies:
            if cookie['domain'][0] != '.':
                cookie['domain'] = '.' + cookie['domain']
            browser.add_cookie(cookie)
        time.sleep(5)

        for search in searchlist:
            browser.get("https://www.glassdoor.com/"+tarlist[0]+"/index.htm")
            #同样要sleep下加载cookie
            browser.find_element_by_css_selector("form input[name='sc.keyword']").send_keys(search)
            browser.find_element_by_css_selector("form button[id='HeroSearchButton']").click()

            # 下拉框选择自动化
            # browser.get("https://www.glassdoor.com/index.htm")
            # browser.find_element_by_css_selector("div[class='context-picker inactive']").click();
            # time.sleep(5)
            # browser.find_element_by_css_selector("div[class='context-picker'] ul[class='context-choice-list'] li[data-search-type='EMPLOYER']").click();
            # time.sleep(5)
            # browser.find_element_by_css_selector("form input[name='sc.keyword']").send_keys(searchlist[0])
            # browser.find_element_by_css_selector("form button[id='HeroSearchButton']").click()

            browser.switch_to.window(browser.window_handles[1])
            url = browser.current_url
            print("HERE-->"+url)
            urllist.append(url)

        browser.quit()
            #print(cookies)
        for search_usl in urllist:
            yield scrapy.Request(search_usl, cookies=cookies, callback=self.parse_page)

        #yield scrapy.Request(url, cookies=cookies, callback=self.parse_page)

    #extract()一定返回数组，注意提取string值。配合extract_first()使用
    def parse_page(self, response):
        que_list = response.css("div[id='InterviewQuestionList'] div[id^='InterviewQuestionResult']")

        for que in que_list:
            content = que.css("table[class='interviewQuestionText'] p[class^='questionText']::text").extract()[0]
            #???better way
            post_date = que.css("div[class='tbl fill margBotSm'] div[class^='cell']::text").extract()[0]
            tag = que.css("span[class='authorInfo'] a::text").extract()[0]
            tag = re.match("^(.*) at (.*) was asked.*$", tag)
            position = tag.group(1)
            company = tag.group(2)

            info = {
                "post_date":post_date,
                "content": content,
                "position": position,
                "company": company,
                "answer": "no_answer",
                "flag": 0
            }
            ans_url = que.css("table[class='interviewQuestionText'] a::attr(href)").extract_first()
            ans_url = parse.urljoin(response.url, ans_url)
            yield scrapy.Request(ans_url, meta=info, callback=self.parse_anwser)

        #next_page
        pages = response.css("div[id='FooterPageNav'] a::attr(href)").extract()
        pages = [parse.urljoin(response.url, url) for url in pages]
        pages = filter(lambda x:True if x.startswith("https") else False, pages)
        for page in pages:
            yield scrapy.Request(page, callback=self.parse_page)


    def parse_anwser(self, response):
        ans_list = response.css("div[id='InterviewQuestionAnswers'] div[class^='comment']")
        info = response.meta
        info["url"] = response.url

        answer = ""
        for ans in ans_list:
            content = ans.css("p[class^='commentText']::text").extract()
            content = "\n".join(content)
            answer = "Ans=====\n"+content
            info["answer"] = answer
            info["flag"] = 1
        yield self.MyItem(info=info)


    def MyItem(self, info):
        #item_loader = ItemLoader(item=GDItem(), response=response)
        gd_item = GDItem()
        gd_item["post_date"] = info["post_date"]
        gd_item["url"] = info["url"]
        gd_item["flag"] = info["flag"]
        gd_item["content"] = info["content"]
        gd_item["company"] = info["company"]
        gd_item["position"] = info["position"]
        gd_item["answer"] = info["answer"]

        return gd_item


    def login(self):
        browser = webdriver.PhantomJS("/Users/emmazhuang/Documents/Python/phantomjs-2.1.1-macosx/bin/phantomjs")
        #browser = webdriver.Chrome(executable_path="/Users/emmazhuang/Documents/Python/chromedriver")

        browser.get("https://www.glassdoor.com/profile/login_input.htm")
        browser.find_element_by_css_selector(".signInForm input[name='username']").send_keys("glasswindow2017em@gmail.com")
        browser.find_element_by_css_selector(".signInForm input[name='password']").send_keys("temp123456")
        browser.find_element_by_css_selector(".signInForm button[id='signInBtn']").click()
        #要sleep,不然cookie会有问题
        time.sleep(5)
        pickle.dump(browser.get_cookies(), open("cookies.pkl", "wb"))
        browser.quit()

    def isLogin(self):

        if not os.path.exists("cookies.pkl"):
            return False
        cookies = pickle.load(open("cookies.pkl", "rb"))
        s=requests.Session()
        for c in cookies:
            s.cookies.set(c['name'], c['value'])
        response=s.get("https://www.glassdoor.com/member/account/resumeUploads_input.htm", headers={'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
}, allow_redirects=False)

        if response.status_code==200:
            return True
        else:
            return False


