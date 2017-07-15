# -*- coding: utf-8 -*-
__author__ = 'emma'

#写一个test先测试一下一小段代码

import redis
redis_cli = redis.StrictRedis()
redis_cli.incr("onem3point_count")
redis_cli.incr("glassdoor_count")

"""
Emmas-MacBook-Pro:redis-3.2.9 emmazhuang$ src/redis-cli 
#运行一次后
127.0.0.1:6379> keys *
1) "onem3point_count"
127.0.0.1:6379> type onem3point_count
string
127.0.0.1:6379> get onem3point_count
"1"
#再运行一次后
127.0.0.1:6379> get onem3point_count
"2"
127.0.0.1:6379> 
"""