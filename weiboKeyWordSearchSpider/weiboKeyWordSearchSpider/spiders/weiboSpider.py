# -*- coding: utf-8 -*-
import scrapy
import os
import re
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
import urllib2
import json
import codecs
import datetime
import time
from pymongo import MongoClient
from urllib import quote_plus


# 程序中有多个sleep，用于加载页面的反应时间
class weiboSpider(scrapy.Spider):
    name = "weiboSpider"

    def __init__(self):
        # 初始化mongo链接
        uri = "mongodb://%s:%s@%s" % (quote_plus('用户名'), quote_plus('密码'), 'ip:port')
        dbClient = MongoClient(uri)
        dbname = "数据库名"
        db = dbClient[dbname]
        self.coll_weiboHighTemperature = db["表名"]
        self.fi = open(r'D:\code\workSpace\pycharm\weiboKeyWordSearchSpider\result\result1.txt', 'w')
        self.fi2 = open(r'D:\code\workSpace\pycharm\weiboKeyWordSearchSpider\result\result2.txt', 'w')
        super(weiboSpider, self).__init__()

    def start_requests(self):

        try:
            # 因为使用phantomjs登陆非常麻烦，所有直接使用selenium进行有界面的环境进行爬取，登录步骤为在用户名和密码进行填写然后点击登录
            browser = webdriver.Chrome()
            browser.get('http://weibo.com/')
            sleep(5)
            # 对用户名和密码的输入框进行填充，然后点击登录按钮
            browser.find_element_by_id('loginname').clear()
            browser.find_element_by_id('loginname').send_keys("chenmo.deyanlei@163.com")
            browser.find_element_by_name('password').clear()
            browser.find_element_by_name('password').send_keys("465212")
            browser.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a').send_keys(Keys.ENTER)
            sleep(10)
            # page需要区分是不是第一页，因为第一页的结构与其他页不同
            divTemp = 0
            start = 0
            end = 0
            for page in range(1, 50):
                # 搜索的关键词 页数
                browser.get('http://s.weibo.com/weibo/摩拜&page=' + str(page))
                sleep(5)
                self.fi.write(str(page) + '\n')
                if page == 1:
                    divTemp = 3
                    start = 1
                    end = 19
                else:
                    divTemp = 1
                    start = 2
                    end = 20

                for item in range(start, end):
                    # text为正文信息，因为可能文字过长存在展开全文选项，需要特别处理
                    # 如果存在链接的话，会出现在该文字下的p标签中
                    try:
                        textLink = browser.find_element_by_xpath(
                            '//*[@id="pl_weibo_direct"]/div/div[' + str(divTemp) + ']/div[' + str(
                                item) + ']/div/div[1]/dl/div/div[3]/div[1]/p/a[1]')
                    except:
                        textLink = 0
                    # 如果p标签下没有该链接选项，则直接获取该标签下的文字，有些字符会出现错误，直接replace掉
                    if textLink == 0:
                        text = browser.find_elements_by_xpath(
                            '//*[@id="pl_weibo_direct"]/div/div[' + str(divTemp) + ']/div[' + str(
                                item) + ']/div/div[1]/dl/div/div[3]/div[1]/p')
                        text = text[0].text.replace(u"#", "").replace(u" ", "").replace(u'&#8203;', "").replace(
                            u'&#nbsp;', "")
                    # 存在链接，但是可能又好几个，有的是各种活动的超级话题，如“#天气#”，所以通过遍历的方法来进行筛选
                    else:
                        for j in range(2, 10):
                            try:
                                # 如果没有action-data，则不断循环，有之后则拿到退出
                                textLink = textLink.get_attribute("action-data")
                                if textLink is None:
                                    textLink = browser.find_element_by_xpath(
                                        '//*[@id="pl_weibo_direct"]/div/div[' + str(divTemp) + ']/div[' + str(
                                            item) + ']/div/div[1]/dl/div/div[3]/div[1]/p/a[' + str(j) + ']')
                                else:
                                    break
                            except:
                                pass
                        # 如果为空取原text值，并做处理
                        if textLink is None:
                            text = browser.find_elements_by_xpath(
                                '//*[@id="pl_weibo_direct"]/div/div[' + str(divTemp) + ']/div[' + str(
                                    item) + ']/div/div[1]/dl/div/div[3]/div[1]/p')
                            text = text[0].text.replace(u"#", "").replace(u" ", "").replace(u'&#8203;', "").replace(
                                u'&#nbsp;', "")
                        # 如果不为空，通过分析网页和请求，获取到链接拼接的字符串并进行拼接，拼接后的url中就是全文信息，请求获得即可
                        else:
                            textLink = "http://s.weibo.com/ajax/direct/morethan140?" + textLink
                            try:
                                resultTemp = urllib2.urlopen(textLink)
                                jsonInfo = resultTemp.read()
                                jsonFile = json.loads(jsonInfo)
                                text = jsonFile['data']['html'].replace(u"#", "").replace(u" ", "").replace(u'&#8203;',
                                                                                                            "").replace(
                                    u'&#nbsp;', "")
                            # 通过尝试，发现新浪有时候自己的链接会为空，手动点击展示全文也无效，这样的话直接取不展开的内容
                            except:
                                try:
                                    text = browser.find_elements_by_xpath(
                                        '//*[@id="pl_weibo_direct"]/div/div[' + str(divTemp) + ']/div[' + str(
                                            item) + ']/div/div[1]/dl/div/div[3]/div[1]/p')
                                    text = text[0].text.replace(u"#", "").replace(u" ", "").replace(u'&#8203;',
                                                                                                    "").replace(
                                        u'&#nbsp;', "")
                                except:
                                    continue
                    text = codecs.escape_decode(codecs.unicode_escape_encode(text)[0])[0]
                    pattern = re.compile(r'\\U.{8}', re.U)
                    text = re.sub(pattern, '', str(text))
                    text = codecs.unicode_escape_decode(text)[0]
                    # 获取位置信息(可能没有)
                    try:
                        location = browser.find_elements_by_xpath(
                            '//*[@id="pl_weibo_direct"]/div/div[' + str(divTemp) + ']/div/div[' + str(
                                item) + ']/div/div[1]/dl/div/div[3]/div[1]/p')
                        location = location.find_element_by_class_name("W_btn_c6")
                        location = location.text.replace(u"&#8203;", "").replace(u"|", "")
                    except:
                        location = 0
                    # 获取用户名
                    userName = browser.find_element_by_xpath(
                        '//*[@id="pl_weibo_direct"]/div/div[' + str(divTemp) + ']/div[' + str(
                            item) + ']/div/div[1]/dl/div/div[3]/div[1]/a[1]')
                    userName = userName.text
                    # 获取用户头像
                    userHead = browser.find_element_by_xpath(
                        '//*[@id="pl_weibo_direct"]/div/div[' + str(divTemp) + ']/div[' + str(
                            item) + ']/div/div[1]/dl/div/div[2]/a/img')
                    userHead = userHead.get_attribute("src")
                    # 获取发送时间
                    sendTime = browser.find_element_by_xpath(
                        '//*[@id="pl_weibo_direct"]/div/div[' + str(divTemp) + ']/div[' + str(
                            item) + ']/div/div[1]/dl/div/div[3]/div[2]/a[1]')
                    sendTime = sendTime.text
                    dt = datetime.datetime.strptime(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
                                                    "%Y-%m-%d %H:%M:%S")
                    # 格式化时间信息，因为有xx秒前、xx分钟前、今天xxx等
                    if u"秒" in sendTime:
                        sendTime = dt + datetime.timedelta(seconds=-int(sendTime.split(u"秒")[0]))
                        sendTime = sendTime.strftime("%Y-%m-%d %H:%M:%S")
                    elif u"分钟" in sendTime:
                        sendTime = dt + datetime.timedelta(minutes=-int(sendTime.split(u"分钟")[0]))
                        sendTime = sendTime.strftime("%Y-%m-%d %H:%M:%S")
                    elif u"今天" in sendTime:
                        sendTime = time.strftime('%Y-%m-%d', time.localtime(time.time())) + " " + sendTime.split(u"今天")[
                            1] + ":00"
                    # 转换为标准时间
                    else:
                        if len(sendTime.split(u"月")[0]) == 1:
                            if len(sendTime.split(u"月")[1].split(u"日")[0]) == 1:
                                sendTime = time.strftime('%Y', time.localtime(time.time())) + "-0" + \
                                           sendTime.split(u"月")[0] + "-0" + sendTime.split(u"月")[1].split(u"日")[
                                               0] + " " + sendTime.split(u"日")[1] + ":00"
                            else:
                                sendTime = time.strftime('%Y', time.localtime(time.time())) + "-0" + \
                                           sendTime.split(u"月")[0] + "-" + sendTime.split(u"月")[1].split(u"日")[
                                               0] + " " + sendTime.split(u"日")[1] + ":00"
                        else:
                            if len(sendTime.split(u"月")[1].split(u"日")[0]) == 1:
                                sendTime = time.strftime('%Y', time.localtime(time.time())) + "-" + \
                                           sendTime.split(u"月")[0] + "-0" + sendTime.split(u"月")[1].split(u"日")[
                                               0] + " " + sendTime.split(u"日")[1] + ":00"
                            else:
                                sendTime = time.strftime('%Y', time.localtime(time.time())) + "-" + \
                                           sendTime.split(u"月")[0] + "-" + sendTime.split(u"月")[1].split(u"日")[
                                               0] + " " + sendTime.split(u"日")[1] + ":00"
                    #使用什么终端发送的微博
                    try:
                        sendFrom = browser.find_element_by_xpath(
                            '//*[@id="pl_weibo_direct"]/div/div[' + str(divTemp) + ']/div[' + str(
                                item) + ']/div/div[1]/dl/div/div[3]/div[2]/a[2]')
                        sendFrom = sendFrom.text
                    except:
                        sendFrom = u"无"
                    # 分享、评论、点赞数(三个数字的结构不一样)
                    shareCount = browser.find_element_by_xpath(
                        '//*[@id="pl_weibo_direct"]/div/div[' + str(divTemp) + ']/div[' + str(
                            item) + ']/div/div[2]/ul/li[2]/a/span/em')
                    shareCount = shareCount.text
                    if len(shareCount) == 0:
                        shareCount = "0"
                    try:
                        commondCount = browser.find_element_by_xpath(
                            '//*[@id="pl_weibo_direct"]/div/div[' + str(divTemp) + ']/div[' + str(
                                item) + ']/div/div[2]/ul/li[3]/a/span/em')
                        commondCount = commondCount.text
                    except:
                        commondCount = "0"
                    goodCount = browser.find_element_by_xpath(
                        '//*[@id="pl_weibo_direct"]/div/div[' + str(divTemp) + ']/div[' + str(
                            item) + ']/div/div[2]/ul/li[4]/a/span/em')
                    goodCount = goodCount.text
                    if len(goodCount) == 0:
                        goodCount = "0"
                    # 插入数据库
                    try:
                        if location == 0:
                            self.coll_weiboHighTemperature.insert(
                                {"userName": userName, "userHead": userHead, "text": text, "sendTime": sendTime,
                                 "sendFrom": sendFrom, "shareCount": shareCount, "commondCount": commondCount,
                                 "goodCount": goodCount})
                            self.fi2.write(
                                userName + '\n' + userHead + '\n' + text + '\n' + sendTime + '\n' + sendFrom + '\n' + shareCount + '\n' + commondCount + '\n' + goodCount + '\n')
                        else:
                            self.coll_weiboHighTemperature.insert(
                                {"userName": userName, "userHead": userHead, "text": text, "sendTime": sendTime,
                                 "sendFrom": sendFrom, "shareCount": shareCount, "commondCount": commondCount,
                                 "goodCount": goodCount, "location": location})
                            self.fi2.write(
                                userName + '\n' + userHead + '\n' + text + '\n' + sendTime + '\n' + sendFrom + '\n' + shareCount + '\n' + commondCount + '\n' + goodCount + '\n' + location + '\n')
                        print str(page) + str(item)
                    except:
                        # 特殊字符多为手机自带的特殊字符
                        print str(page) + str(item)
                sleep(5)
        except BaseException, e:
            self.logger.error("ERROR : start  " + repr(e))
            self.close(self.name, repr(e))
