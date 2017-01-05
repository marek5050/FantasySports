#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.shell import inspect_response
from scrapy.selector import Selector
from bs4 import BeautifulSoup

import math
import datetime
now = datetime.datetime.now()


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

        
class InjurySpider(scrapy.Spider):
    name = 'injurySpider'
    start_urls = ['http://www.rotoworld.com/teams/injuries/nba/all/']
    

    def parse(self, response):        
        num = 0
        injuries = []
        tables = response.css('div.pb')
        # Header information
        injuries.append(tables[0].css("tr")[0].css("td b::text").extract())
        for table in tables:
            # Team Abbreviation
            teamRaw = table.xpath('.//div[@class="headline"]/@style').extract()[0]
            teamIdxStart = teamRaw.index('icons/')+6
            teamIdx = teamRaw.index('.gif')
            team = teamRaw[teamIdxStart:teamIdx]
            
            for row in table.css("tr")[1:]:
                yield  {
                        'team':team,
                        'player': row.css("td::text, td a::text, div::text").extract()
                     }
        return

class NBATargets(scrapy.Spider):
    name = 'NBATargets'
    start_urls = [
#'https://playbook.draftkings.com/nba/nba-targets-january-3rd-2'
'https://playbook.draftkings.com/nba/nba-targets-$MONTH-$DAY-2'.replace("$MONTH",now.strftime("%B")).replace("$DAY", ordinal(now.day))
,'https://playbook.draftkings.com/nba/nba-cheat-sheet-$MONTH-$DAY-2'.replace("$MONTH",now.strftime("%B")).replace("$DAY", ordinal(now.day))
]
    
    def cheatSheet(self, response):
        print("cheatSheet")
        items = response.css("p strong")
        i = 0 
        newType = None
        org = []
        for item in items:
            text = item.css("::text").extract()[0]
            if "BEST" in text:
                newType = "BEST"
            elif "WORST" in text:
                newType = "WORST"
            elif "vs." in text and newType!=None:
                org.append({"value":(2 if newType == "BEST" else -1), "name":text.split("($")[0].strip()})
                newType = None
            else:
                org.append({"value":1 , "name": text})                        
        return org
        
    def targets(self, page):
        print('targets')
        targetss = page.css('p strong').extract()
        clean = []
        for t in targetss:
            if not "Other Options" in t and not "Note:" in t and not "WATCH:" in t:
                name = t.split("($")
                soup = BeautifulSoup(t)
                name = soup.get_text().split("($")
                clean.append({"value": 1,"name": name[0].strip()})
        return clean

    def parse(self, response):        
        header = response.css('h2')[0].extract()
        community = []
        if 'NBA Targets' in header:
            print("NBA Targets")
            yield {
                   'targets': self.targets(response)
                   }
        else:
             yield {
                     'cheatsheet': self.cheatSheet(response)            
                    }        
        return

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
        
    def parse(self, response):        
        header = response.css('h2')[0].extract()
        community = []
        yield {
               'stats': self.getStats(response)
               }        
        return
  
    
    