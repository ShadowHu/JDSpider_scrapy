# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
from JDSpider_scrapy import settings
import time
import logging

logger = logging.getLogger()

class JdspiderScrapyPipeline(object):
    def __init__(self):
        self.connect = pymysql.connect(
            host=settings.MYSQL_HOST,
            db=settings.MYSQL_DBNAME,
            user=settings.MYSQL_USER,
            passwd=settings.MYSQL_PASSWD,
            charset='utf8')
        self.cursor = self.connect.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()

    def process_item(self, item, spider):
        sql = '''INSERT INTO JDTest (itemUrl, pid, insertTime, title, cateid, brand, shop, categories, images, ptable, params, price, priceInfo, description, stock) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s");''' % \
        (item['itemUrl'][0], 
        item['pid'][0], 
        int(time.time()), 
        self.connect.escape(str(item['title'][0].lstrip().rstrip())), 
        item['cateid'][0], 
        self.connect.escape(str(item['brand'][0])), 
        self.connect.escape(str(item['brand'][2])), 
        self.connect.escape(str(item['categories'])), 
        self.connect.escape(str(item['images'])), 
        self.connect.escape(str(item['ptable'][0])), 
        self.connect.escape(str(item['params'])), 
        item['price'][0], 
        self.connect.escape(str(item['priceInfo'])), 
        self.connect.escape(str(item['description'])), 
        self.connect.escape(str(item['stock']))
        )
        try:
            self.cursor.execute(sql)
            self.connect.commit()
        except pymysql.err.IntegrityError:
            pass
        except Exception as err:
            # print(sql)
            self.connect.rollback()
            logging.log(logging.ERROR, err)
        else:
            logger.info('Insert successful')
            return item
