# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess


import datetime
from datetime import date
now = datetime.datetime.now()


import math
ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])


class NBATargets(scrapy.Spider):
    name = 'NBATargets'
    start_urls = [
#'https://playbook.draftkings.com/nba/nba-targets-january-3rd-2'
'https://playbook.draftkings.com/nba/nba-targets-$MONTH-$DAY'.replace("$MONTH",now.strftime("%B")).replace("$DAY", ordinal(now.day))
,'https://playbook.draftkings.com/nba/nba-cheat-sheet-$MONTH-$DAY'.replace("$MONTH",now.strftime("%B")).replace("$DAY", ordinal(now.day))
]
#    outputDirectory = "targets"

 #   def update_settings(self,settings):
 #       settings.set('FEED_URI','data/'+self.outputDirectory+'/'+str(date.today())+'.json')
 #       return settings
        
    def cheatSheet(self, response):
        print("cheatSheet")
        items = response.css("p strong")
        newType = None
        org = []
        for item in items:
            text = item.css("::text").extract()[0]
            if "BEST" in text:
                newType = "BEST"
            elif "WORST" in text:
                newType = "WORST"
            elif "vs." in text and newType!=None:
                org.append({"value":(3 if newType == "BEST" else -2), "name":text.split("($")[0].strip()})
                newType = None
            else:
                if "($" in text:
                    text = text.split("($")[0]

                org.append({"value":2 , "name": text.strip()})
        return org
        
    def targets(self, page):
        print('targets')
        targetss = page.css('h3,p').extract()
        clean = []
        val = 0
        for t in targetss:
            if "Other Options" in t:
                #'<p><strong>Other Options –</strong> Russell Westbrook ($12,300), Jeff Teague ($7,400), Dennis Schröder ($6,600)</p>'
                names = t.split("\u2013")[1]
                names = names.split("),")
                for name in names: 
                    soup = BeautifulSoup(name)
                    name = soup.get_text().split("($")[0]
                    if "$" in name:
                        name= name.split("$")[0]
                    name = name.replace("\u00f6","o")
                    clean.append({"value":2, "name":name.strip()})
                val = 0
                pass
            elif "Note:" in t:
                val = 0
            elif "WATCH:" in t:                
                val = 0
            elif "Stud" in t:
                val = 4
                pass
            elif "Value" in t:
                val = 3
                pass
    
            soup = BeautifulSoup(t)
            name = soup.get_text()
            if val > 0 and not (name == "Stud" or name =="Studs" or name == "Value"):
                    if "($" in name:
                        name = name.split("($")[0]

                    if "\u2013" in name:
                         name = name.split("\u2013")[0]

                    if "@" in name:
                        name = name.split("@")[0]

                    if "vs." in name:
                        name = name.split("vs.")[0]

                    clean.append({"value": val,"name": name.strip()})

        return clean

    def parse(self, response):        
        header = response.css('h2')[0].extract()
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

if __name__ == "__main__":
    print("Starting recommendation extraction.")
    targetsProcess = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': 'data/targets/' + str(date.today()) + '.json'
    })

    targetsProcess.crawl(NBATargets)
    targetsProcess.start()
    print("Finished recommendations. ")