# -*- coding: utf-8 -*-
import scrapy
import os
import re
from selenium import webdriver
import traceback
from time import sleep
from selenium.webdriver.common.keys import Keys
import urllib2
from lxml import etree
import json

browser = webdriver.Chrome()
browser.get('http://s.weibo.com/weibo/%25E9%25AB%2598%25E6%25B8%25A9&Refer=index')

# textLink = browser.find_element_by_xpath('//*[@id="pl_weibo_direct"]/div/div[1]/div[3]/div[2]/div[1]/dl/div/div[3]/div[1]/p/a[2]')
# print textLink
# textLink = textLink.get_attribute("action-data")





try:
    textLink = browser.find_element_by_xpath('//*[@id="pl_weibo_direct"]/div/div[1]/div[3]/div[2]/div[1]/dl/div/div[3]/div[1]/p/a[2]')
except:
    textLink = 0


if textLink == 0:
    text = "++++++++++++++++++++++"
else:
    text = textLink.get_attribute("action-data")

print text