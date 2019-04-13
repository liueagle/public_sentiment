# -*- coding: utf-8 -*-
import scrapy
import datetime
from baiduspider.items import BaiduspiderItem
from .. import TimeCalculate
from .. import TimeMarch
from .. import ChildPage
from .. import read_json

class JdwxggSpider(scrapy.Spider):
    name = 'jdwxgg'
    allowed_domains = ['www.jdwx.info']
    start_urls = ['http://www.jdwx.info/forum-29-1.html']
    allowed_timesup = 10  # 最多超过时限次数
    if(read_json.read_json(name)):
        default_scope_day = 50 #首次爬取时限
    else:
        default_scope_day = 30 #增量爬取时限


    def parse(self, response):
        nodelist = response.xpath('//tbody/tr/th')#得到一页中的所有帖子
        item = BaiduspiderItem()
        isHasContent = False  # 判断此页中是否有合适的信息
        NextPageUrl = ''
        timecount = 0  # 计数器
        for node in nodelist:#分析帖子信息\
            childUrl = node.xpath("./a[2][@class='s xst']/@href").extract_first()
            item["title"]= node.xpath("./a[2][@class='s xst']/text()").extract_first()
            item["UrlId"] = node.xpath("./a[2][@class='s xst']/@href").extract_first()
            if (childUrl != None):
                item["info"] = ChildPage.ChildPage(childUrl,'2')
            item["time"] = node.xpath('./a[2]/../../td[@class="by"]/em/span/text()').extract_first()

            if item["time"] == None:
                item["time"] = node.xpath('./a[2]/../../td[@class="by"]/em/span/span/text()').extract_first()
            #处理时间为空的情况
            if item["time"] == None:
                item["time"] = ''
            else:
                item["time"] = item["time"].strip()
                item["time"] = TimeCalculate.time_calculate(item["time"], self.name)
            # 判断这个帖子是否符合时间
            if(TimeMarch.time_March(item["time"],self.default_scope_day)==True):
                item["IsLimitedTime"] = 'y'
            else:
                item["IsLimitedTime"] = 'n'
                timecount = timecount + 1
            if(NextPageUrl == ''):#记录下一页的链接
                NextPageUrl = response.xpath('//div[@class="pg"]/a[@class="nxt"]/@href').extract_first()
            if item["UrlId"] != None:  # 非普通帖子的错误处理（置顶帖等异常的帖子）
                yield item #返回数据到pipeline
        if(timecount>self.allowed_timesup):#根据判断决定继续爬取还是结束
             self.crawler.engine.close_spider(self, 'Finished')#关闭爬虫
        else:
            yield scrapy.Request(NextPageUrl,callback = self.parse)

