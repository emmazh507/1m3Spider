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
        searchlist = ['huawei']
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
        #同样要sleep下加载cookie
        time.sleep(5)
        browser.find_element_by_css_selector("form input[name='sc.keyword']").send_keys(searchlist[0])
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
        #browser.quit()
        #print(cookies)

        yield scrapy.Request(url, cookies=cookies, callback=self.parse_page)

        #yield scrapy.Request(url, cookies=cookies, callback=self.parse_page)


    def parse_page(self, response):
        print(response.status)

        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x:True if x.startswith("https") else False, all_urls)

        for url in all_urls:
            # if the page is to a question
            match_obj = re.match("(.*glassdoor.com/Interview/.*(QTN_\d+).htm$.*)", url)
            if match_obj:
                que_url = match_obj.group(1)
                question_id = match_obj.group(2)
                yield scrapy.Request(que_url, meta={"question_id":question_id}, callback=self.parse_question)

            else:
                #keep crawl if its page url
                pass
                # page_object = re.match("(.*glassdoor.com/Interview/.*(IP\d+).htm$.*)", url)
                # if page_object:
                #     page_url = page_object.group(1)
                #     print("next+page-->"+page_url)
                #     yield scrapy.Request(url, callback=self.parse_page)
                # else:
                #     pass


    def parse_question(self, response):
        print(response.text)
        pass






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


