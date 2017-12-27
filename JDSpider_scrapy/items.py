# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field

class JDItem(scrapy.Item):
    # define the fields for your item here like:
    cateid = Field()
    itemUrl = Field()
    pid = Field()
    title = Field()
    brand = Field()
    categories = Field()
    images = Field()
    ptable = Field()
    params = Field()
    price = Field()
    priceInfo = Field()
    description = Field()
    stock = Field()
    # commentUrl = Field()
    # commentJson = Field()
    # afterCount = Field()
    # averageScore = Field()
    # commentCount = Field()
    # defaultGoodCount = Field()
    # generalCount = Field()
    # generalRate = Field()
    # goodCount = Field()
    # goodRate = Field()
    # poorCount = Field()
    # poorRate = Field()
    # showCount = Field()
    # hotCommentTagStatistics = Field()
    # comment_onepage = Field()