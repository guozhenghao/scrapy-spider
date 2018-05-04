# coding:utf-8

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import re
import time
from scrapy import log
from pymongo import MongoClient
from PM25.getLatLon import getLatLon
from scrapy.exceptions import DropItem
from urllib import quote_plus

class rankPagePipeline(object):

    def __init__(self):
        uri = "mongodb://%s:%s@%s" % (quote_plus('用户名'), quote_plus('密码'), 'ip:port')
        dbClient  = MongoClient(uri)
        dbname = "数据库名"
        self.db = dbClient[dbname]
        self.city_pm_info = "城市信息表名"
        self.point_pm_info = "站点信息表名"
        self.getLatLon = getLatLon()

    def process_item(self, item,spider):
        for key in item:
            if len(item[key]):
                item[key] = item[key][0].encode("utf-8")
            else:
                item[key] = ""
        self.process_convtype(item)
        item["dimDate"] = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        item["dimHour"] = time.strftime('%H', time.localtime(time.time()))
        item["updateDate"] = time.strftime('%Y-%m-%d %H', time.localtime(time.time()))+":00:00"
        cityInfo = self.getLatLon.transAmap(item["city"],log)
        item["city"] = cityInfo["city"]
        item["province"] = cityInfo["province"]
        item["lon"] = cityInfo["lon"]
        item["lat"] = cityInfo["lat"]
        # 插入数据库
        if item["pageLevel"] == 1:
            coll = self.db[self.city_pm_info]
            coll.insert(item)
        if item["pageLevel"] == 2:
            item["district"] = cityInfo["district"]
            coll = self.db[self.point_pm_info]
            coll.insert(item)
        return item

    def process_convtype(self,item):
        # 转换数据类型
        item['pageLevel'] = int(item['pageLevel'])
        item['aqi'] = int(item['aqi'])
        item['pm25'] = float(item['pm25'])
        item['pm_10'] = float(item['pm_10'])
        item['co'] = float(item['co'])
        item['no2'] = float(item['no2'])
        item['o3'] = float(item['o3'])
        item['o3_8'] = float(item['o3_8'])
        item['so2'] = float(item['so2'])
