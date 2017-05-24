#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import scrapy
from scrapy.selector import Selector

import datetime
from scrapy.crawler import CrawlerProcess


now = datetime.datetime.now()
from datetime import date


ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

# http://www.basketball-reference.com/teams/NOP/2017.html
# http://prolinestadium.sportsdirectinc.com/basketball/nba-matchups.aspx?page=/data/NBA/matchups/g5_summary_12.html
# http://www.covers.com/pageLoader/pageLoader.aspx?page=/data/nba/matchups/g5_summary_12.html
# NJN = BRK, NOH=NOP, CHA = CHO
'''
    teams = ["ATL","BOS","BRK","CHO","CHI","CLE","DAL",
             "DEN","DET","GSW","HOU","IND","LAC","LAL","MEM",
             "MIA","MIL","MIN","NOP","NYK","OKC","ORL","PHI",
             "PHO","POR","SAC","SAS","TOR","UTA","WAS"]
'''
class ReferenceSpider(scrapy.Spider):
    name = 'blogspider'
    teams = ["ATL","BOS","BRK","CHO","CHI","CLE","DAL",
             "DEN","DET","GSW","HOU","IND","LAC","LAL","MEM",
             "MIA","MIL","MIN","NOP","NYK","OKC","ORL","PHI",
             "PHO","POR","SAC","SAS","TOR","UTA","WAS"]
    start_urls = ['http://www.basketball-reference.com/teams/TEAMID/2017.html'.replace("TEAMID",team) for team in teams ]
#    outputDirectory = "teams"
    
#    def update_settings(self,settings):
#        settings.set('FEED_URI','data/'+self.outputDirectory+'/'+str(date.today())+'.json')
#        return settings
        
    def parseTable(self, num,table):
        table = Selector(text=table)
        rows = table.css('tr')
        tableRows = []
        for row in rows: 
            columns = row.css("th,td")
            vals = []
            for col in columns:
                text = col.css("::text").extract_first()
                if(text == None):
                    text = ""
                vals.append(text)
            tableRows.append(vals)
        
        return {table.xpath("//@id").extract_first(): tableRows}  
    

    def parse(self, response):
        url = response.request.url
        team  = url.split("/")[4]
        
        num = 0
        tables = []
        for table in response.css('.table_wrapper'):
            num += 1
            data =  table.extract()
            data = data.replace("<!--","").replace("-->","")
            tables.append(self.parseTable(num,data))    

        yield {
             "team"  : team,
             "data"  : tables
        }
        return



if __name__ == "__main__":
    print("Starting team data extraction.")
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': 'data/teams/' + str(date.today()) + '.json'
    })

    process.crawl(ReferenceSpider)
    process.start()
    print("Finished team data extraction.")
