# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
from JDSpider_scrapy import settings
import time
import logging
import sys


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
        (item['itemUrl'], 
        item['pid'], 
        int(time.time()), 
        self.connect.escape(str(item['title'][0].lstrip().rstrip())), 
        item['cateid'], 
        self.connect.escape(str(item['brand'][0])), 
        self.connect.escape(str(item['shop'][0])), 
        self.connect.escape(str(item['categories'])), 
        self.connect.escape(str(item['images'])), 
        self.connect.escape(str(item['ptable'][0])), 
        self.connect.escape(str(item['params'])), 
        item['price'], 
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
            # self.connect.rollback()
            self.cursor.close()
            self.connect.close()
            logging.log(logging.ERROR, err)
            sys.exit("SHUT DOWN EVERYTHING!")
        else:
            logger.info('Insert successful')
            return item

class JdspiderCommentPipeline(object):
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
        for c in item['comments']:
            sql = '''INSERT INTO JDCommentTest (pid, commentUrl, commentJson, afterCount, averageScore, commentCount, defaultGoodCount, generalCount, generalRate, goodCount, goodRate, poorCount, poorRate, showCount, hotCommentTagStatistics, InsertTime, comment, guid, commentTime, userId, userName, commentContent, userScore) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s");''' % \
                (item['pid'],
                item['commentUrl'],
                self.connect.escape(str(item['commentJson'])),
                item['afterCount'],
                item['averageScore'],
                item['commentCount'],
                item['defaultGoodCount'],
                item['generalCount'],
                item['generalRate'],
                item['goodCount'],
                item['goodRate'],
                item['poorCount'],
                item['poorRate'],
                item['showCount'],
                item['hotCommentTagStatistics'],
                int(time.time()),
                self.connect.escape(str(c['content'])),
                c['guid'],
                int(time.mktime(time.strptime(c['creationTime'], '%Y-%m-%d %H:%M:%S'))),
                c['id'],
                c['nickname'],
                self.connect.escape(str(c)),
                c['score']
            )
            
            try:
                self.cursor.execute(sql)
                self.connect.commit()
            except pymysql.err.IntegrityError:
                pass
            except Exception as err:
                # print(sql)
                # self.connect.rollback()
                # self.cursor.close()
                # self.connect.close()
                sys.exit("SHUT DOWN EVERYTHING!")
                logging.log(logging.ERROR, err)
            else:
                logger.info('Insert successful')
        return item