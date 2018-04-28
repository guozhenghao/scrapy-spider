# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

# 第三层界面抓取，得到邮编和在这个邮编下的所有地区
class ZipcodespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    zipCode = scrapy.Field()
    place = scrapy.Field()
    _id = scrapy.Field()

