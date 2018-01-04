#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-01-02 13:37:31
# @Author  : Shadow Hu (shadow_hu1441@163.com)
# @GitHub    : https://github.com/ShadowHu
# from JDSpider_scrapy.items import JDCommentItem
import scrapy
from scrapy import Request
import json, re
from JDSpider_scrapy.items import JDCommentItem
import pymysql
from JDSpider_scrapy import settings
import sys


COMMENT_URL = "http://club.jd.com/comment/skuProductPageComments.action?score=0&sortType=6&pageSize=10&isShadowSku=0&fold=1&page=1&productId="

class JDSpiderComment(scrapy.Spider):
    name  = 'jdcom'
    custom_settings = {
        'ITEM_PIPELINES': {
            'JDSpider_scrapy.pipelines.JdspiderCommentPipeline':  400
        }
    }

    def __init__(self):
        self.connect = pymysql.connect(
                host=settings.MYSQL_HOST,
                db=settings.MYSQL_DBNAME,
                user=settings.MYSQL_USER,
                passwd=settings.MYSQL_PASSWD,
                charset='utf8')
        self.cursor = self.connect.cursor()

    def __del__(self):
        self.cursor.close()
        self.connect.close()

    def start_requests(self):
        sql = "SELECT pid FROM JDTest"
        self.cursor.execute(sql)
        startUrl = COMMENT_URL + self.cursor.fetchone()[0]
        yield Request(startUrl, callback=self.parse)

    def fetch_url(self):
        try:
            itemurl = COMMENT_URL + self.cursor.fetchone()[0]
        except TypeError:
            sys.exit("Complete!")
        else:
            return itemurl

    def parse(self, response):
        js = json.loads(response.body_as_unicode())
        page = int(re.search(r'page=(\d+)', response.url).group(1))
        if page > 99 or js['comments'] == []: # process next item
            # print('next item')
            yield Request(self.fetch_url(), callback=self.parse)
        else:
            item = JDCommentItem()
            item['pid'] = str(re.search(r'productId=(\d+)', response.url).group(1))
            item['commentUrl'] = response.url
            item['commentJson'] = js
            item['afterCount'] = js['productCommentSummary']['afterCount']
            item['averageScore'] = js['productCommentSummary']['averageScore']
            item['commentCount']= js['productCommentSummary']['commentCount']
            item['defaultGoodCount']= js['productCommentSummary']['defaultGoodCount']
            item['generalCount']= js['productCommentSummary']['generalCount']
            item['generalRate']= js['productCommentSummary']['generalRate']
            item['goodCount']= js['productCommentSummary']['goodCount']
            item['goodRate']= js['productCommentSummary']['goodRate']
            item['poorCount']= js['productCommentSummary']['poorCount']
            item['poorRate']= js['productCommentSummary']['poorRate']
            item['showCount']= js['productCommentSummary']['showCount']
            item['hotCommentTagStatistics'] = js['hotCommentTagStatistics']
            item['comments'] = js['comments']
            yield item
            next_url = re.sub(r'page=(\d+)', 'page='+str(page+1), response.url)
            yield Request(next_url, callback=self.parse)