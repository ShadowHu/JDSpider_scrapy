# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
from JDSpider_scrapy import settings
import time

class JdspiderScrapyPipeline(object):
    def __init__(self):
        self.connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            db=settings.MYSQL_DBNAME,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWD,
            charset='utf8',
            use_unicode=True)
        self.cursor = self.connect.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()

    def process_item(self, item, spider):
        sql = '''INSERT INTO JDTest (itemUrl, pid, insertTime, title, cateid, brand, categories, images, ptable, params, price, priceInfo, description, stock) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s");''' % \
        (item['itemUrl'], 
        item['pid'], 
        int(time.time()), 
        self.connect.escape(str((item['title']))), 
        item['cateid'], 
        self.connect.escape(str((item['brand']))), 
        self.connect.escape(str((item['categories']))), 
        self.connect.escape(str((item['images']))), 
        self.connect.escape(str((item['ptable']))), 
        self.connect.escape(str((item['params']))), 
        item['price'], 
        self.connect.escape(str((item['priceInfo']))), 
        self.connect.escape(str((item['description']))), 
        self.connect.escape(str((item['stock']))))
        try:
            self.cursor.execute(sql)
            self.connect.commit()
        except Exception as err:
            print(sql)
            raise err
        else:
            return item
