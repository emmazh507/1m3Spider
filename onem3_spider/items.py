# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
import redis
from models.es_types import MjType
from w3lib.html import remove_tags

from elasticsearch_dsl.connections import connections
es = connections.create_connection(MjType._doc_type.using)

redis_cli = redis.StrictRedis()

class MJItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    post_date = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()
    suggest = scrapy.Field()

    def save_to_es(self):
        mj = MjType()
        mj.url = self['url']
        mj.title = self['title']
        if "tags" in self:
            mj.tags = self['tags']
        content = "".join(self["content"])
        mj.content = remove_tags(content)
        #mj.meta.id==XXX 可以通过meta.id来设置es中存放设置的item id
        mj.suggest = gen_suggests(MjType._doc_type.index, ((mj.title, 10),(mj.content, 2)))
        mj.save()
        #记录每种item的爬取数量
        redis_cli.incr("onem3point_count")


class GDQueItem(scrapy.Item):
    post_date = scrapy.Field()
    url = scrapy.Field()
    company = scrapy.Field()
    position = scrapy.Field()
    content = scrapy.Field()
    answer_number = scrapy.Field()
    question_id = scrapy.Field()


class GDAnsItem(scrapy.Item):
    post_date = scrapy.Field()
    question_id = scrapy.Field()
    content = scrapy.Field()




def gen_suggests(index, info_tuple):#tuple可以传递多个值
    #根据字符串生成搜索建议数组
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            #调用es的analyze接口分析字符串 GET _analyze {"analyzer":"xxx", "text":"xxxx"}
            words = es.indices.analyze(index=index, analyzer="ik_max_word", params={'filter':["lowercase"]}, body=text)
            analyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"])>1]) #python的列表生成式
            new_words = analyzed_words - used_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input":list(new_words), "weight":weight})

    return suggests











