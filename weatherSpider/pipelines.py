# -*- coding: utf-8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from pymongo import MongoClient
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy import log

class MongoDBPipeline(object):
    def __init__(self):
        dbClient  = MongoClient("111.111.111.111",111)
        dbname = "national_regionalism"
        db = dbClient[dbname]
        self.coll = db["weather"]

    def process_item(self,item,spider):
       try:
           for key in item:
            if len(item[key]):
                item[key] = item[key][0].encode("utf-8")
                if item[key] == "_" and key != "primary_Pollutant":
                    item[key] = 0
            else:
                item[key] = ""
       except BaseException, e:
            log.msg(repr(e),log.WARNING)           
    
