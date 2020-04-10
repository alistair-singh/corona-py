#!/bin/python3

CONFIRMED_URL="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
DEATHS_URL="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
RECOVERED_URL="https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"

import httplib2
import csv
import io
import pprint
import datetime
import collections

httpClient = httplib2.Http('.cache')
def download_file(url):
    global httpClient
    response, content = httpClient.request(url)
    with io.StringIO(content.decode("utf-8")) as strIO:
        reader = csv.reader(strIO)
        return tuple(row for row in reader)
        
confirmed = download_file(CONFIRMED_URL)
deaths = download_file(DEATHS_URL)
recovered = download_file(RECOVERED_URL)

print(f"rows confirmed={len(confirmed)} deaths={len(deaths)} recovered={len(recovered)}")

def report(region, country, confirmed, deaths, recovered):
    DayRecord = collections.namedtuple('DayRecord', 
            'date confirmed confirmed_delta deaths deaths_delta recovered recovered_delta')
    start = datetime.date(2020,1,22)
    days_c = [c for c in confirmed if c[1] == country and c[0] == region][0][4:]
    days_d = [c for c in deaths if c[1] == country and c[0] == region][0][4:]
    days_r = [c for c in recovered if c[1] == country and c[0] == region][0][4:]
    days = [ (start+datetime.timedelta(days=day_num), tc, td, tr)
            for (day_num, tc, td, tr) 
            in zip(range(len(days_c)), days_c, days_d, days_r)]

    for (today, previous) in ((d, d-1) for d in range(len(days))):
        if previous < 0: previous = 0
        today_date, tc, td, tr = days[today]
        _, pc, pd, pr = days[previous]
        yield DayRecord(date=today_date, 
                confirmed=int(tc), 
                confirmed_delta=int(tc) - int(pc), 
                deaths=td, 
                deaths_delta=int(td)-int(pd), 
                recovered=tr, 
                recovered_delta=int(tr)-int(pr))

def printReport(region, country):
    for (today, c, dc, d, dd, r, dr) in report(region, country, confirmed, deaths, recovered):
        print(f"{today} {c:>6} {dc:>6} {d:>6} {dd:>6} {r:>6} {dr:>6}")

printReport('', 'South Africa')
