import datetime
import json
import os
from datetime import date
from datetime import timezone

import scrapy
from scrapy.crawler import CrawlerProcess


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


now = datetime.datetime.utcnow()

ordinal = lambda n: "%d%s" % (n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])


class GameInjurySpider(scrapy.Spider):
    name = 'gameInjurySpider'
    outputDirectory = "injuries"
    home = "none"
    away = "none"

    def start_requests(self):
        yield scrapy.Request('http://www.rotoworld.com/teams/injuries/nba/', self.parse)

    def parse(self, response):
        injuries = []
        tables = response.css('div.pb')

        for table in tables:
            # Team Abbreviation
            injuries.append(table.css("tr")[0].css("td b::text").extract())

            teamRaw = table.xpath('.//div[@class="headline"]/@style').extract()[0]
            teamIdxStart = teamRaw.index('icons/') + 6
            teamIdx = teamRaw.index('.gif')
            team = teamRaw[teamIdxStart:teamIdx]
            for row in table.css("tr")[1:]:
                playerInfo = row.css("td::text, td a::text, div::text").extract()
                playerInfo = playerInfo.append(team)
                yield playerInfo
        return


def send_mail(text_msg):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    gmailUser = 'marek.bejda@gmail.com'
    gmailPassword = 'snowGMhawk123$$!'
    recipient = 'marek.bejda@gmail.com'
    message = text_msg

    msg = MIMEMultipart()
    msg['From'] = gmailUser
    msg['To'] = recipient
    msg['Subject'] = "Fantasy injuries for today"
    msg.attach(MIMEText(json.dumps(message)))

    mailServer = smtplib.SMTP('smtp.gmail.com', 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(gmailUser, gmailPassword)
    mailServer.sendmail(gmailUser, recipient, msg.as_string())
    mailServer.close()


def scrape():
    previous_file = 'data/injuries/' + str(date.today()) + '.json'
    try:
        with open(previous_file) as json_data:
            previous_injuries = json.load(json_data)
        os.remove(previous_file)
    except:
        print("Failed to load previous injuries")
        previous_injuries = []

    injuryProcess = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_FORMAT': 'json',
        'FEED_URI': 'data/injuries/' + str(date.today()) + '.json'
    })

    injuryProcess.crawl(GameInjurySpider)
    injuryProcess.start()

    current_file = 'data/injuries/' + str(date.today()) + '.json'
    try:
        with open(current_file) as json_data:
            current_injuries = json.load(json_data)
    except:
        print("Failed to load current injuries")
        current_injuries = []

    if len(current_injuries) > len(previous_injuries):
        print("There's new injuries!! ")
        send_mail(current_injuries)
    else:
        print("less or same, file hasn't changes")



if __name__ == "__main__":
    print("Starting injury extraction.")

    # calendar_file = "./GoldenState_2017_calendar.json"
    # try:
    #     with open(calendar_file) as json_data:
    #         calendar = json.load(json_data)
    # except:
    #     print("Failed to load calendar file.")
    #     calendar = []
    #
    # df = pd.DataFrame.from_dict(calendar["games"])
    # df['dateTime'] = pd.to_datetime(df['dateTimeUTC'])
    # current_game = df[df["complete"] == False].iloc[0]
    #
    # home = 'gsw'
    # away = current_game['opponent']['abbrev']
    scrape()