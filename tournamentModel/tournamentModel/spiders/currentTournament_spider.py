import scrapy

class currentTournamentSpider(scrapy.Spider):
    name = "currentTournament"
    def start_requests(self):
        urls = [
            'https://www.sports-reference.com/cbb/postseason/2021-ncaa.html'
        ]

        for url in urls:
            yield scrapy.Request(url=url,callback=self.parse)
    
    def parse(self,response):
        gamesSelector = response.xpath("//div[@id='bracket']/div[@class='round']/div")
        for selector in gamesSelector:
            emptyTeams = selector.xpath("div/span[@class='note']/em").getall()
            otherTeams = selector.xpath("div/a")
            for team in otherTeams:
                teamName = team.xpath("text()").get()
                relativeUrl = team.attrib['href']
                request =  response.follow(relativeUrl, callback=self.parse_stats)
                request.cb_kwargs['inputTeam'] = teamName
                request.cb_kwargs['inputYear'] = 2021
                yield request
    def parse_stats(self,response,inputTeam,inputYear):
        t = response.xpath("//table[@id='schools_conf_per_game']//tr")
        i = 0
        for r in t:
            if i in (0,2,4):
                i+=1
                continue
            i+=1

            d = r.xpath("td")
            statNames = d.xpath("@data-stat").getall()
            statValues = d.xpath("text()").getall()
            print(inputTeam,inputYear)
            print(statNames)
            print(statValues)
            sn = str(statValues)
            sn = sn.replace("'","").replace("[","(").replace("]",")")
            #print(len(d))
            #for data in d:
                #print(data.xpath("@data-stat").getall())
                #print(data.xpath('text()').getall())