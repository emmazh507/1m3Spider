# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import codecs
import MySQLdb
import MySQLdb.cursors

from twisted.enterprise import adbapi

class Onem3SpiderPipeline_Json(object):
    #__init__初始化
    def __init__(self):
        self.file = codecs.open('mj_info.json', 'w', encoding='utf-8')
    #默认执行process_item
    def process_item(self, item, spider):
        #ensure_ascii=False-->否则中文显示不正常
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        #要return回去，可能别的地方还要用
        return item

    def spider_closed(self, spider):
        self.file.close()

#同步
class Onem3SpiderPipeline_sql(object):
    def __init__(self):
        self.conn = MySQLdb.connect('localhost', 'root', '', 'onem3_spider', charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into mj(url, title, tags, content)
            VALUES (%s, %s, %s, %s)
        """
        test_sql = """
            insert into mj(test)
            VALUE (%s)
        """

        tags = ",".join(item["tags"])
        title = "".join(item["title"])
        content = "".join(item["content"])

        print(content)
        self.cursor.execute(insert_sql, [item['url'][0], title, tags, content])

        #self.cursor.execute(insert_sql, [item['url'], item['title'], item['tags'], item['content']])
        #self.cursor.execute(test_sql, ["haha"]) # values must be iterablbe, use [] even has only one value, must be a tuple (search,) or a list [search]
        #self.cursor.execute("INSERT INTO mj (test, content) VALUES ('test', 'why not display???');")
        self.conn.commit()

#异步
class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    #scrapy will call it in initialize stage
    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            #name should be the same as connection.py
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            charset = 'utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        # ** is a shortcut that allows you to pass multiple arguments to a function directly using either a list/tuple or a dictionary.
        # equals to adbapi.ConnectionPool("MySQLdb", host=settings["MYSQL_HOST"], db=settings["MYSQL_DBNAME"]......)
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        #使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        #处理异步插入的异常
        query.addErrback(self.handle_error)

    def handle_error(self, failure):
        print (failure)

    def do_insert(self, cursor, item):
        #从dbpool中取了一个cursor
        insert_sql = """
            insert into mj(url, title, tags, content) 
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content)
        """

        tags = ",".join(item["tags"])
        title = "".join(item["title"])
        content = "".join(item["content"])

        cursor.execute(insert_sql, [item['url'][0], title, tags, content])



