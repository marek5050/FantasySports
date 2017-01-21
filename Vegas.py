# -*- coding: utf-8 -*-

import scrapy
from datetime import date

import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.http import FormRequest, Request

now = datetime.datetime.now()

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

class VegasItem(scrapy.Item):
    team = scrapy.Field()
    odds = scrapy.Field()
    overUnder = scrapy.Field()

class VegasOdds(scrapy.Spider):
    name = 'VegasOdds'

    start_urls = ['http://www.espn.com/nba/lines']

    def parse(self, response):

        heads = response.css("table.tablehead").css("tr.stathead")
        for match in heads:
            home = VegasItem()
            away = VegasItem()
            items = match.xpath("following-sibling::tr[2]").css("td")
            #items[0] # Name
            #items[1] # Odds + -
            text = items[1].css("::text").extract()
            if "EVEN" in text:
                home["odds"] = 1
                away["odds"] = 1
            elif len(text) == 4:
                home["odds"] = text[0]
                away["odds"] = text[1]
                home["team"] = (text[2].split(":")[0])[0:3].replace("PHX","PHO").replace("WSH","WAS")
                away["team"] = (text[3].split(":")[0])[0:3].replace("PHX","PHO").replace("WSH","WAS")

            text = items[5].css("::text").extract()
            if len(text) == 1:
                home["overUnder"] = text[0]
                away["overUnder"] = text[0]
            yield home
            yield away



if __name__ == "__main__":
    print("Starting DvP extraction.")
    injuryProcess = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'data/vegas/' + str(date.today()) + '.csv'
    })

    injuryProcess.crawl(VegasOdds)
    injuryProcess.start()