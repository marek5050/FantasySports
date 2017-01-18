# -*- coding: utf-8 -*-

import scrapy
from datetime import date

import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.http import FormRequest, Request

now = datetime.datetime.now()

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

class DefenseItem(scrapy.Item):
    team = scrapy.Field()
    g = scrapy.Field()
    all = scrapy.Field()
    pg = scrapy.Field()
    sg = scrapy.Field()
    sf = scrapy.Field()
    pf = scrapy.Field()
    c = scrapy.Field()

class DefenseVsPosition(scrapy.Spider):
    name = 'DefenseVsPosition'

    start_urls = ['https://basketballmonster.com/dfsdvp.aspx']

    def parseTable(self, response):
        print(response)
        result = []
        rows = response.css("div.dvp-div").css("tr")
        for row in rows:
            cells = row.css("th::text, a::text , td::text").extract()
            if "vs" in cells[0]:
                item = DefenseItem()
                t = cells[0].split(" ")[1]
                if "NOR" in t:
                    t = "NO"
                elif "SAS" in t:
                    t = "SA"
                elif "NYK" in t:
                    t = "NY"
                elif "GSW" in t:
                    t = "GS"
                item["team"] = t
                item["g"] = cells[1]
                item["all"] = cells[2]
                item["pg"] = cells[3]
                item["sg"]= cells[4]
                item["sf"]  = cells[5]
                item["pf"] = cells[6]
                item["c"] = cells[7]
                yield item

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formdata={'DAILYTYPEDROPDOWN': '4'},
            method="POST",
            callback=self.parseTable
        )

if __name__ == "__main__":
    print("Starting DvP extraction.")
    injuryProcess = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'data/Defense/' + str(date.today()) + '.csv'
    })

    injuryProcess.crawl(DefenseVsPosition)
    injuryProcess.start()