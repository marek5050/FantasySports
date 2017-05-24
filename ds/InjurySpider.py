# -*- coding: utf-8 -*-

import scrapy
from datetime import date

import datetime

from scrapy.crawler import CrawlerProcess

now = datetime.datetime.now()

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

class InjurySpider(scrapy.Spider):
    name = 'injurySpider'
    start_urls = ['http://www.rotoworld.com/teams/injuries/nba/all/']
    outputDirectory = "injuries"

#    def update_settings(self,settings):
#        settings.set('FEED_URI','data/'+self.outputDirectory+'/'+str(date.today())+'.json')
#        return settings

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

import pandas as pd
import glob

class AllInjurySpider(scrapy.Spider):
    name = 'AllInjurySpider'
    start_urls = ['http://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate=2016-12-$DAY&EndDate=2016-12-$DAY&InjuriesChkBx=yes&PersonalChkBx=yes&Submit=Search'.replace("$DAY",str(x)) for x in range(1,32)]
    outputDirectory = "injuries"

    #    def update_settings(self,settings):
    #        settings.set('FEED_URI','data/'+self.outputDirectory+'/'+str(date.today())+'.json')
    #        return settings
 #   def start_requests(self):
 #       'http://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate=2016-12-01&EndDate=2017-01-31&InjuriesChkBx=yes&PersonalChkBx=yes&Submit=Search'

    def grabInjuries(self, response):
        injuries = ",".join(response.css("table.datatable tr td:nth-child(4n)::text").extract()).replace(" • ","").split(",")
        return injuries


    def parse(self, response):
        path = r'data/output/'  # use your path
        allFiles = glob.glob(path + "/*.csv")
        for _file in allFiles:
            try:
                _date = _file.split("/")[2].split(".csv")[0]
                if "_" in _date:
                    _date = _date.split("_")[0]
                injuries = self.grabInjuries(response)
                df = pd.read_csv("data/output/" + _date + ".csv", header=0, index_col=None)

                for injury in injuries:
                    df.loc[(df.Name == injury)]["injury"] = 1.0
            except Exception as e :
                print("Some error")
                print(e)
                raise

        return


if __name__ == "__main__":
    print("Starting injury extraction.")
    injuryProcess = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': 'data/injuries/' + str(date.today()) + '.json'
    })

    injuryProcess.crawl(InjurySpider)
    injuryProcess.start()