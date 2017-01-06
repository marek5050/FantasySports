# -*- coding: utf-8 -*-

from datetime import date
from scrapy.crawler import CrawlerProcess
from ReferenceSpider import ReferenceSpider as rs
from InjurySpider import InjurySpider
from NBATargets import NBATargets as targets
from GoldStats import  GoldStats

'''
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_FORMAT': 'json',
    'FEED_URI': 'data/temp/'+str(date.today())+'.json'
})
process.crawl(ReferenceSpider)
#process.crawl(InjurySpider)
#process.crawl(NBATargets)
#process.crawl(GoldStats)
process.start()
'''
'''
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_FORMAT': 'json',
    'FEED_URI': 'data/teams/'+str(date.today())+'.json'
})

process.crawl(rs)
process.start()

'''

injuryProcess = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_FORMAT': 'json',
    'FEED_URI': 'data/injuries/'+str(date.today())+'.json'
})

injuryProcess.crawl(InjurySpider)
injuryProcess.start()

'''
targetsProcess = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_FORMAT': 'json',
    'FEED_URI': 'data/targets/'+str(date.today())+'.json'
})

targetsProcess.crawl(targets)
targetsProcess.start()
'''
'''
targetsProcess = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_FORMAT': 'json',
    'FEED_URI': 'data/goldstats/'+str(date.today())+'.json'
})

targetsProcess.crawl(GoldStats)
targetsProcess.start()
'''

print("Done")