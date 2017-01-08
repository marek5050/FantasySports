# -*- coding: utf-8 -*-

import scrapy
from datetime import date

import datetime

from scrapy.crawler import CrawlerProcess

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains


now = datetime.datetime.now()

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

class InjurySpider(scrapy.Spider):
    name = 'injurySpider'
    start_urls = ['http://www.fantasylabs.com/nba/news/']
    outputDirectory = "news"

#    def update_settings(self,settings):
#        settings.set('FEED_URI','data/'+self.outputDirectory+'/'+str(date.today())+'.json')
#        return settings
    def __init__(self):
        self.driver = webdriver.PhantomJS()

    def parse(self, response):
        injuries = []
        tables = response.css('div.pb')
        # Header information
        for table in tables:
            header = table.css("a::text")
            playerName = header[0]
            # Team Abbreviation
            team =   header[1]
            report = table.css("div.report")
            impact = table.css("div.impact")
            if "start" in report:
                start = 1
            else:
                start = 0
            yield  {
                    'player':playerName,
                    'team': team,
                    'report' : report,
                    'impact': impact,
                    'start': start
                 }
        next_page = response.css('li.next a::attr(href)').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

        return

if __name__ == "__main__":
    print("Starting injury extraction.")
    injuryProcess = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': 'data/news/' + str(date.today()) + '.json'
    })

    injuryProcess.crawl(InjurySpider)
    injuryProcess.start()