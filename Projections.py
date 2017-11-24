import glob
from datetime import date
from io import StringIO

import requests
from bs4 import BeautifulSoup

today = str(date.today())
end_date = today
#
#
# output_file = "data/predictions/"+today+".csv"
#
# if os.path.isfile(output_file):
#
#        url = 'https://swishanalytics.com/optimus/nba/daily-fantasy-projections'
#        r = requests.get(url)
#
#        start = r.text.index("this.players = [{")+len("this.players = [{")-2
#        end = r.text.index("this.currentSite",start)
#
#        io = StringIO(r.text[start:end].strip()[0:-1])
#        s = json.load(io)
#
#        print(s)
#        k = pd.DataFrame(s)
#        headers =  ['assists', 'blocks', 'date', 'dk_avg', 'dk_fpts', 'dk_fpts_act',
#               'dk_fpts_ingame', 'dk_pos', 'dk_pos2', 'dk_salary', 'dk_value',
#               'double_double', 'event_id', 'event_status_id',
#               'home', 'minutes', 'name', 'nickname', 'opp_abbr', 'player_id',
#               'points', 'primary_pos_abbr', 'rebounds', 'steals', 'three_made',
#               'turnovers', 'votes']
#        k = k[headers]
#        k.to_csv(output_file, sep=',', encoding='utf-8', index=False, float_format='%.3f')
#
# k = pd.read_csv(output_file)
# k.set_index("name",inplace=True)
#
# vs = pd.read_csv("data/final/" + today+".csv")
#
# for idx, row in vs.iterrows():
#        if row["Name"] in k:
#               vs.loc[idx, "proj"] = k.loc[row["Name"]]["dk_fpts"]
#        else:
#               vs.loc[idx, "proj"] = row["AvgPointsPerGame"]
# vs.to_csv("data/predictions/final_" + today+".csv", sep=',', encoding='utf-8', index=False, float_format='%.3f')
# print("popcorn")
#
# name = 'AllInjurySpider'
# start_urls = [
#        'http://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate=2016-12-$DAY&EndDate=2016-12-$DAY&InjuriesChkBx=yes&PersonalChkBx=yes&Submit=Search'.replace(
#               "$DAY", str(x)) for x in range(1, 32)]
# outputDirectory = "injuries"


#    def update_settings(self,settings):
#        settings.set('FEED_URI','data/'+self.outputDirectory+'/'+str(date.today())+'.json')
#        return settings
#   def start_requests(self):
#       'http://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate=2016-12-01&EndDate=2017-01-31&InjuriesChkBx=yes&PersonalChkBx=yes&Submit=Search'


def grabInjuries(_date):
       url = 'http://www.prosportstransactions.com/basketball/Search/SearchResults.php?Player=&Team=&BeginDate=$DATE&EndDate=$DATE&InjuriesChkBx=yes&PersonalChkBx=yes&Submit=Search'.replace("$DATE",_date)
       r = requests.get(url)
       page = BeautifulSoup(r.text)
       #injuries =  ",".join(page.css("table.datatable tr td:nth-child(4n)::text").extract()).replace(" • ","").split(",")
       injuries = []
       for row in  page.find_all("tr"):
              injuries.append(row.find_all("td")[3].text.replace(" • ","").strip())
       return injuries

#
# path = r'data/output/'  # use your path
# allFiles = glob.glob(path + "/*.csv")
# for _file in allFiles:
#        try:
#               _date = _file.split("/")[2].split(".csv")[0]
#               if "_" in _date:
#                      _date = _date.split("_")[0]
#               injuries = grabInjuries(_date)
#               df = pd.read_csv("data/output/" + _date + ".csv", header=0, index_col=None)
#
#               for injury in injuries:
#                      df.loc[(df.Name == injury)]["injury"] = 1.0
#               print(df)
#        except Exception as e:
#               print("Some error")
#               print(e)
#               raise
# print("HEloworld")


from calculate import *

def grabSalariesForDays(days):

    import datetime

    now = datetime.datetime.now()

    ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(n/10%10!=1)*(n%10<4)*n%10::4])

    base = datetime.datetime.today()
    date_list = [base - datetime.timedelta(days=x) for x in range(0, days)]
    datelist = pd.date_range(pd.datetime.today(), periods=days).tolist()

    for current_date in date_list:
        _date = current_date.strftime("%Y-%m-%d")
        url = "https://swishanalytics.com/optimus/nba/daily-fantasy-salary-changes?date="+_date

        r = requests.get(url)
        try:
            start = r.text.index("this.players_dk = [{")+len("this.players_dk = [{")-2
            end = r.text.index(" this.players_fd",start)

            st = r.text[start:end].replace("console.log(this.players_dk);","").strip()[0:-1].strip()

            io = StringIO(st)
            s = json.load(io)

            k = pd.DataFrame(s)
            k.to_csv("data/newSalaries/"+_date+'.csv', sep=',', encoding='utf-8', index=False,float_format='%.3f')
        except Exception as e:
            print("failed to get date" + _date)
            print(_date)

def fixSalaries():
    path = r'data/newSalaries/'  # use your path
    allFiles = glob.glob(path + "/*.csv")
    for _file in allFiles:
       try:
            _date = _file.split("/")[2].split(".csv")[0]
            print("Processing salaries for date " + _date )
            if "_" in _date:
                _date = _date.split("_")[0]
            df = pd.read_csv(_file)
            del df["salary_change_html"]
            df.to_csv(_file, sep=',', encoding='utf-8', index=False, float_format='%.3f')
            print("Finished processing salaries for date " + _date)
       except Exception as e:
           print("Error with date: " + _date)
           print(e)
           raise

#fixSalaries()