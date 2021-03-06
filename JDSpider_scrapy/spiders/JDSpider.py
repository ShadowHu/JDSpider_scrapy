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
    custom_settings = {
        'ITEM_PIPELINES': {
            'JDSpider_scrapy.pipelines.JdspiderScrapyPipeline':  400
        }
    }

    def parse(self, response): # process start_url and callback to parse all cate
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

    def parse_allcate(self, response): # process all cates pages and callback to parse every cate page
        maxpage = int(response.xpath('//span[@class="fp-text"]/i/text()')[0].extract())
        for p in range(1, maxpage+1):
            cateurl = response.url + '&page=' + str(p)
            yield Request(cateurl, callback=self.parse_cate)

    def parse_cate(self, response): # process every cate page and callback to parse item
        nodes = response.xpath('//div[@id="plist"]//div[@class="p-img"]/a/@href')
        for node in nodes:
            itemurl = 'http:' + node.extract() if node.extract()[:4] != 'http' else node.extract()
            yield Request(itemurl, callback=self.parse_item)

    def parse_item(self, response):
        item=JDItem()
        itemld = ItemLoader(item=item, response=response)
        cate = re.search(r'cat: \[(\d{2,5}),(\d{2,5}),(\d{2,5})\]', response.body_as_unicode())
        cateid = 'cat=' + str(cate.group(1)) + ',' + str(cate.group(2)) + ',' + str(cate.group(3))
        # print(cateid)
        item['cateid'] = cateid

        item['itemUrl'] =  response.url
        try:
            pid = re.search('com/\d+', response.url).group(0)[4:]
        except AttributeError:
            pid = re.search('hk/\d+', response.url).group(0)[3:]
        item['pid'] = pid
        itemld.add_xpath('title', '//div[@class="sku-name"]//text()')
        itemld.add_xpath('brand', '//ul[@id="parameter-brand"]/li/@title')
        itemld.add_xpath('brand', '//div[@class="p-parameter"]/ul/li/a/text()')
        itemld.add_xpath('shop', '//div[@class="popbox-inner"]//h3//a/@title')
        itemld.add_xpath('categories', '//div[@id="crumb-wrap"]/div/div/div/a/text()')
        itemld.add_xpath('images', '//div[@id="spec-list"]/ul/li/img/@src')
        itemld.add_xpath('ptable', '//div[@class="p-parameter"]/ul/li')
        itemld.add_xpath('params', '//ul[@class="parameter2 p-parameter-list"]/li/text()')
        itemld.load_item()
        yield Request(PRICE_URL+pid, callback=self.parse_price, meta={'item': item})

    def parse_price(self, response):
        item = response.meta['item']
        js = json.loads(response.body_as_unicode())
        while True:
            try:
                item['price'] = js[0]['p']
            except KeyError:
                yield Request(PRICE_URL+item['pid'], callback=self.parse_price, meta={'item': item})
            else:
                break
        item['priceInfo'] = response.body_as_unicode()
        yield Request(STOCK_URL + item['pid'] + '&' + item['cateid'], callback=self.parse_stock, meta={'item': item})

    def parse_stock(self, response):
        item = response.meta['item']
        item['stock'] = response.body.decode('gbk')
        yield Request(DESC_URL + item['pid'] + '&' + item['cateid'] + '&_=' + str(int(time.time()*1000)), callback=self.parse_desc, meta={'item': item})
        # yield item

    def parse_desc(self,response):
        item = response.meta['item']
        # itemld = response.meta['itemld']
        item['description'] = response.body.decode('gbk')
        yield item

    
