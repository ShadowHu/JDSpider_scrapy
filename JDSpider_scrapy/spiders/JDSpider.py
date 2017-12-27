#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-12-26 15:27:01
# @Author  : Shadow Hu (shadow_hu1441@163.com)
# @GitHub    : https://github.com/ShadowHu

import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader
from JDSpider_scrapy.items import JDItem
import re, time, json
import logging

DESC_URL = "http://cd.jd.com/promotion/v2?area=1_72_2799_0&shopId=1000087348&venderId=1000087348&isCanUseDQ=isCanUseDQ-1&isCanUseJQ=isCanUseJQ-1&skuId="
PRICE_URL = "http://p.3.cn/prices/mgets?type=1&area=1_72_2799_0&pdtk=&pduid=15026999298361111775083&pdpin=&pin=%s&pdbp=0&ext=11000000&source=item-pc&skuIds=J_"
STOCK_URL = "http://c0.3.cn/stock?area=1_72_2799_0&venderId=1000087348&buyNum=1&choseSuitSkuIds=&extraParam={%22originid%22:%221%22}&ch=1&fqsp=0&pduid=15026999298361111775083&pdpin=&detailedAdd=%s&skuId="
COMMENT_URL = "http://club.jd.com/comment/skuProductPageComments.action?score=0&sortType=6&page=0&pageSize=10&isShadowSku=0&fold=1&productId="

FOOD_TAG = "secondtype|keycount|allfenlei|flmc_14"



class JDSpider(scrapy.Spider):
    name = "jd"
    start_urls = ["http://www.jd.com/allSort.aspx"]


    def parse(self, response):
        if not FOOD_TAG:
            nodes = response.xpath('//div[@class="items"]/dl/dd/a/@href')
            for node in nodes:
                url = 'http:' + node.extract() if node.extract()[:4] != 'http' else node.extract()
                yield Request(url)
        else:
            nodes = response.xpath('//div[@clstag="' + FOOD_TAG + '"]/dl/dd/a/@href')
            for node in nodes:
                url = 'http:' + node.extract() if node.extract()[:4] != 'http' else node.extract()
                yield Request(url, callback=self.parse_allcate)

    def parse_allcate(self, response): # return all cate page
        maxpage = int(response.xpath('//span[@class="fp-text"]/i/text()')[0].extract())
        for p in range(1, maxpage+1):
            cateurl = response.url + '&page=' + str(p)
            yield Request(cateurl, callback=self.parse_cate)

    def parse_cate(self, response):
        nodes = response.xpath('//div[@id="plist"]//div[@class="p-img"]/a/@href')
        for node in nodes:
            itemurl = 'http:' + node.extract() if node.extract()[:4] != 'http' else node.extract()
            yield Request(itemurl, callback=self.parse_item)

    def parse_item(self, response):
        itemObj = ItemLoader(item=JDItem(), response=response)
        cate = re.search(r'cat: \[(\d{2,5}),(\d{2,5}),(\d{2,5})\]', response.body_as_unicode())
        cateid = 'cat=' + str(cate.group(1)) + ',' + str(cate.group(2)) + ',' + str(cate.group(3))
        # print(cateid)
        itemObj.add_value('cateid', cateid)

        itemObj.add_value('itemUrl', response.url)
        try:
            pid = re.search('com/\d+', response.url).group(0)[4:]
        except AttributeError:
            pid = re.search('hk/\d+', response.url).group(0)[3:]
        itemObj.add_value('pid', pid)
        itemObj.add_xpath('title', '//div[@class="sku-name"]//text()')
        itemObj.add_xpath('brand', '//ul[@id="parameter-brand"]/li/@title')
        itemObj.add_xpath('brand', '//div[@class="p-parameter"]/ul/li/a/text()')
        itemObj.add_xpath('categories', '//div[@id="crumb-wrap"]/div/div/div/a/text()')
        itemObj.add_xpath('images', '//div[@id="spec-list"]/ul/li/img/@src')
        itemObj.add_xpath('ptable', '//div[@class="p-parameter"]/ul/li')
        itemObj.add_xpath('params', '//ul[@class="parameter2 p-parameter-list"]/li/text()')
        yield Request(PRICE_URL+pid, callback=self.parse_price, meta={'item': itemObj})
        yield Request(STOCK_URL + pid + '&' + cateid, callback=self.parse_stock, meta={'item': itemObj})
        yield Request(DESC_URL + pid + '&' + cateid + '&_=' + str(time.time()*1000), callback=self.parse_desc, meta={'item': itemObj})
        return itemObj.load_item()

    def parse_price(self, response):
        itemObj = response.meta['item']
        js = json.loads(response.body_as_unicode())
        itemObj.add_value('price', js[0]['p'])
        itemObj.add_value('priceInfo', response.body_as_unicode())
        return itemObj.load_item()

    def parse_stock(self, response):
        itemObj = response.meta['item']
        itemObj.add_value('stock', response.body.decode('gbk'))
        return itemObj.load_item()

    def parse_desc(self,response):
        itemObj = response.meta['item']
        itemObj.add_value('description', response.body.decode('gbk'))
        return itemObj.load_item()
    
