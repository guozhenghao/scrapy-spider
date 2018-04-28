# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
from scrapy import log
from pymongo import MongoClient
from scrapy.exceptions import DropItem
from scrapy.exporters import JsonItemExporter
import os

class ZipcodespiderPipeline(object):
    def process_item(self, item, spider):
        return item

class JobJsonItemExporter(JsonItemExporter):
    ''' 序列化前的处理 '''
    def serialize_field(self, field, name, value):
        ''' 对每个字段，value的每个元素都进行处理 '''
        
        return super(JobJsonItemExporter, self).serialize_field(field, name, value)

class JobspiderPipeline(object):
    ''' JobspiderPipeline '''
    def __init__(self):
        
        # 连接数据库
        # 你的地址和端口号
        dbClient  = MongoClient("111.111.111.111",11111)
        dbname = "national_regionalism"
        db = dbClient[dbname]
        self.coll = db["zipCode"]

        # result3路径
        filepath = os.getcwd()
        self.itemFile = file(filepath+r'\zipCodeSpider\result\result3.txt', 'wb')
        # JsonItemExporter 默认指定为 ensure_ascii 编码，改为 gbk 后解决
        self.exporter = JobJsonItemExporter(self.itemFile, encoding='gbk')
        
    def process_item(self, item, spider):
        ''' process_item'''       
        try:
            # 写入文件
            self.exporter.export_item(item)
            # 插入数据库
            self.coll.insert(item)
        except BaseException, e:
            log.msg(repr(e),log.WARNING) 
          
        return item
