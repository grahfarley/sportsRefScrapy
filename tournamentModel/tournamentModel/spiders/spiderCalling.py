#call spider from script
from scrapy.crawler import CrawlerProcess
from previousTournament_spider import previousTournamentSpider

process = CrawlerProcess()
process.crawl(previousTournamentSpider)
process.start()