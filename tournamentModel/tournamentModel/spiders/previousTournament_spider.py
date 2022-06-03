import scrapy
import re
from writingToDb import writeToDatabase,lookupTeamAndYear,writeTeamStatsByYear
class previousTournamentSpider(scrapy.Spider):
    name = "previousTournament"
    def start_requests(self):
        urls  = [f'https://www.sports-reference.com/cbb/postseason/{n}-ncaa.html' for n in range(2011,2022)]
        for url in urls: 
            year = int(re.findall("20[012][0-9]",url)[0])
            if year == 2020:
                continue
            request = scrapy.Request(url=url,callback=self.parse)
            request.cb_kwargs['responseYear'] = year
            yield request
    

    def parse(self,response,responseYear):
        #print(responseYear)
        gamesSelector = response.xpath("//div[@id='bracket']/div[@class='round']/div")
        gameNum = 0
        for selector in gamesSelector:
            matchup = selector.xpath("div/span[@class='note']/em/text()|div/a/text()").getall()
            if len(matchup) == 1:
                continue
            if len(matchup) == 2: 
                leftTeam  = matchup[0].replace("'","").replace("(","").replace(")","").replace(".","")
                rightTeam = matchup[1].replace("'","").replace("(","").replace(")","").replace(".","")
                leftTeamScore = 'NULL'
                rightTeamScore = 'NULL'
            if len(matchup) == 4:
                leftTeam  = matchup[0].replace("'","").replace("(","").replace(")","").replace(".","")
                rightTeam = matchup[2].replace("'","").replace("(","").replace(")","").replace(".","")
                leftTeamScore  = matchup[1]
                rightTeamScore = matchup[3]
            if leftTeam == 'tbd' and rightTeam == 'tbd':
                continue
            writeToDatabase(responseYear,leftTeam,leftTeamScore,rightTeam,rightTeamScore,gameNum)
            gameNum += 1
            actualTeams = selector.xpath("div/a")
            i = 0
            for team in actualTeams:
                if i in (1,3) and responseYear < 2021:
                    i+=1
                    continue
                i+=1
                teamName = team.xpath("text()").get().replace("'","").replace("(","").replace(")","").replace(".","")
                c = lookupTeamAndYear(teamName,responseYear)
                if c > 0:
                    continue
                relativeUrl = team.attrib['href']
                request2 =  response.follow(relativeUrl, callback=self.parse_stats)
                request2.cb_kwargs['inputTeam'] = teamName
                request2.cb_kwargs['inputYear'] = responseYear
                yield request2

    def parse_stats(self,response,inputTeam,inputYear):
        t = response.xpath("//table[@id='schools_conf_per_game']//tr")
        print(inputTeam)
        print(len(t))
        i = 0
        concatStats = []
        for r in t:
            if i in (0,2,4):
                i+=1
                continue
            i+=1

            d = r.xpath("td")
            statNames = d.xpath("@data-stat").getall()
            statValues = d.xpath("text()").getall()
            concatStats = concatStats + statValues
        for i in range(0,len(concatStats)):
            concatStats[i] = float(concatStats[i])
        
        teamNameForList = "'"+inputTeam+"'"
        concatStats.insert(0,inputYear)
        concatStats.insert(0,inputTeam)
        sn = tuple(concatStats)
        print((sn))
        
        writeTeamStatsByYear(inputTeam,inputYear,sn)