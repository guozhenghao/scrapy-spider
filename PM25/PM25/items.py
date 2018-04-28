# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class rankPageItems(scrapy.Item):
    # 排序值，二级页面沿用其父页面的
    rank = scrapy.Field()
    # 标记一级/二级页面
    pageLevel = scrapy.Field()
    _id = scrapy.Field()
    cityId = scrapy.Field()
    pointId = scrapy.Field()    
    # 抓取时间戳
    dimDate = scrapy.Field()
    dimHour = scrapy.Field()
    # 网站更新时间戳
    updateDate = scrapy.Field()
    city = scrapy.Field()
    aqi = scrapy.Field()
    air_mark = scrapy.Field()
    primary_Pollutant = scrapy.Field()
    pm25 = scrapy.Field()
    pm_10 = scrapy.Field()
    co = scrapy.Field()
    no2 = scrapy.Field()
    o3 = scrapy.Field()
    o3_8 = scrapy.Field()
    so2 = scrapy.Field()

