# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeatherspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    cityCode = scrapy.Field()
    temp = scrapy.Field()
    SD = scrapy.Field()
    updateTime = scrapy.Field()
    WD = scrapy.Field()
    WSE = scrapy.Field()
    quality = scrapy.Field()


