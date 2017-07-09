# -*- coding: utf-8 -*-
__author__ = 'emma'

from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, InnerObjectWrapper, Completion, Keyword, Text
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=["localhost"])

class MjType(DocType):
    # content = scrapy.Field(
    #     input_processor=
    # )
    url = Keyword()
    title = Text(analyzer="ik_max_word")
    tags = Keyword()
    content = Text(analyzer="ik_max_word")

    class Meta:
        index = "onem3point"
        doc_type = 'mj'


if __name__ == "__main__":
    MjType.init() #根据定义的类直接生成索引信息