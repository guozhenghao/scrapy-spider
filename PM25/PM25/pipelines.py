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
        uri = "mongodb://%s:%s@%s" % (quote_plus('root'), quote_plus('密码'), 'ip:port')
        dbClient  = MongoClient(uri)
        dbname = "数据库名"
        self.db = dbClient[dbname]
        self.city_pm_info = "pm25in_city_pm_info"
        self.point_pm_info = "pm25in_point_pm_info"
        self.getLatLon = getLatLon()
        

    def process_item(self, item, spider):
        # log.msg("TEST: "+ str(item),log.ERROR)
        for key in item:
            if key is "_id":
                continue
            if len(item[key]):
                item[key] = item[key][0].encode("utf-8")
                if item[key] == "_" and key != "primary_Pollutant":
                    item[key] = 0
            else:
                item[key] = ""
        self.process_PP(item)
        # self.process_UpdateDate(item)
        self.process_convtype(item)
        item["dimDate"] = time.strftime('%Y%m%d', time.localtime(time.time()))
        item["dimHour"] = time.strftime('%H', time.localtime(time.time()))
        item["updateDate"] = time.strftime('%Y-%m-%d %H', time.localtime(time.time()))+":00:00"

        # self.exporter.export_item(item)

        # log.msg(item, log.WARNING)

        # 插入数据库
        if item["pageLevel"] == 1:
            coll = self.db[self.city_pm_info]
            self.getLatLon.process_city(item,log)
            coll.insert(item)
        if item["pageLevel"] == 2:
            coll = self.db[self.point_pm_info]
            self.getLatLon.process_point(item,log)
            coll.insert(item)
        return item

    def process_convtype(self,item):
        # PM 10 可吸入颗粒物 可能情况： 数字，_
        item['pageLevel'] = int(item['pageLevel'])
        if item['pageLevel'] == 1:
            item['rank'] = int(item['rank'])
        item['aqi'] = int(item['aqi'])
        item['pm25'] = float(item['pm25'])
        item['pm_10'] = float(item['pm_10'])
        item['co'] = float(item['co'])
        item['no2'] = float(item['no2'])
        item['o3'] = float(item['o3'])
        item['o3_8'] = float(item['o3_8'])
        item['so2'] = float(item['so2'])

    def process_PP(self,item):
        ''' 处理 Primary_Pollutant 为多行的情况 '''
        PPStr = item["primary_Pollutant"]
        # log.msg(PPStr, log.INFO)
        if len(PPStr):
            PPStr = PPStr.replace("\\n","").replace(" ","")
            item["primary_Pollutant"] = PPStr

    def process_UpdateDate(self, item):
        UpdateDateStr = item["updateDate"]
        if len(UpdateDateStr):
            UpdateDateStr = UpdateDateStr.replace(u'数据更新时间：'.encode("utf-8"), "")
            # UpdateDateStr = time.mktime(time.strptime(UpdateDateStr,"%Y-%m-%d %H:%M:%S"))
            item["updateDate"] = UpdateDateStr

