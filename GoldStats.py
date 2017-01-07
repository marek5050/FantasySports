#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import scrapy
from bs4 import BeautifulSoup
from datetime import date

import datetime
from scrapy.crawler import CrawlerProcess


now = datetime.datetime.now()


ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

class GoldStats(scrapy.Spider):
    name = 'NBAGoldStats'
    start_urls = ['http://www.dfsgold.com/nba/draftkings-daily-position-cheat-sheet']
    
    def getStats(self, response):
        data = [] 
        for row in response.css("tr"):  
            row_values = [] 
            for cell in row.css("td"):
                soup = BeautifulSoup(cell.extract())
                cell_values = soup.get_text()
                row_values.append(cell_values)
            data.append(row_values)
                    
        return data
    
    def update_settings(self,settings):
        settings.set('FEED_URI','data/'+self.outputDirectory+'/'+str(date.today())+'.json')
        return settings

    def parse(self, response):        
        yield {
               'stats': self.getStats(response)
               }        
        return

if __name__ == "__main__":
    print("Starting goldstats extraction.")
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': 'data/goldstats/' + str(date.today()) + '.json'
    })

    process.crawl(GoldStats)
    process.start()
    print("Finished goldstats extraction.")

  

