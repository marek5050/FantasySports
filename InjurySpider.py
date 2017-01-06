# -*- coding: utf-8 -*-

import scrapy
from datetime import date

import datetime
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