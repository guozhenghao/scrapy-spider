# coding:utf-8

import scrapy
import re
import os
from weatherSpider.items import WeatherspiderItem
import json
from pymongo import MongoClient
import time

class baseSpider(scrapy.Spider):
    
    name = "baseSpider"

    def __init__(self):
        filepath = os.getcwd()
        self.fi = open(filepath+r'\result\result.txt','w')
        super(baseSpider,self).__init__()

        dbClient  = MongoClient("47.92.6.177",27017)
        dbname = "national_regionalism"
        db = dbClient[dbname]
        self.coll = db["weather"]

    def start_requests(self):
        try:
            url = 'http://cj.weather.com.cn/support/detail.aspx?id=51837fba1b35fe0f8411b6df'
            yield scrapy.Request(url, callback=self.parse_basePage)
        except BaseException, e:
            self.logger.error("ERROR")
            self.close(self.name, repr(e))
        else:
            self.logger.warning("--SCRAPY: crawl over correctly")
            self.close(self.name, "crawl over")

    def parse_basePage(self,response):
        i = 2
        # fi = open(r"D:\VSCode\workspace\weatherSpider\result\body.htm",'w')
        # fi.write(response.body)
        # fi.close()
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        weatherItem = WeatherspiderItem()
        while i < 4100:
            weatherItem["cityCode"] = response.xpath("/html/body/div[2]/div/div[2]/div/div/p[" + str(i) +"]/text()").extract()
            i += 1
            if len(weatherItem["cityCode"]) == 0 :
                break
            pattern = re.compile(r'\d{9}',re.M)
            cityCode = pattern.search(weatherItem["cityCode"][0]).group()
            url = "http://www.weather.com.cn/data/sk/" + cityCode.encode('utf-8') + ".html"
            yield scrapy.Request(url, callback=self.parse_secondPage)
        yield weatherItem

    def parse_secondPage(self,response):
       
        try:
            self.fi.write(response.body+"\n")
            jsonfile = json.loads(response.body) 
            jsonfile = jsonfile["weatherinfo"]
            jsonfile["createDate"]=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            # self.MongoInsert(jsonfile)
        except BaseException, e:
            self.logger.error("ERROR")
            self.close(self.name, repr(e))

    def MongoInsert(self,item):
        self.coll.insert(item)