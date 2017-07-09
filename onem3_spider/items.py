# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from models.es_types import MjType
from w3lib.html import remove_tags

class MJItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    tags = scrapy.Field()
    content = scrapy.Field()

    def save_to_es(self):
        mj = MjType()
        mj.url = self['url']
        mj.title = self['title']
        if "tags" in self:
            mj.tags = self['tags']
        content = "".join(self["content"])
        mj.content = remove_tags(content)
        #mj.meta.id==XXX 可以通过meta.id来设置es中存放设置的item id
        mj.save()

