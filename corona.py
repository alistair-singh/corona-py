#!/bin/python3

import httplib2
import csv
import io
import pprint
import datetime
import collections

CONFIRMED_URL = ("https://raw.githubusercontent.com"
                 "/CSSEGISandData/COVID-19/master"
                 "/csse_covid_19_data/csse_covid_19_time_series"
                 "/time_series_covid19_confirmed_global.csv")
DEATHS_URL = ("https://raw.githubusercontent.com"
              "/CSSEGISandData/COVID-19/master"
              "/csse_covid_19_data/csse_covid_19_time_series"
              "/time_series_covid19_deaths_global.csv")
RECOVERED_URL = ("https://raw.githubusercontent.com"
                 "/CSSEGISandData/COVID-19/master"
                 "/csse_covid_19_data/csse_covid_19_time_series"
                 "/time_series_covid19_recovered_global.csv")

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

print((f"rows "
       f"confirmed={len(confirmed)} "
       f"deaths={len(deaths)} "
       f"recovered={len(recovered)}"))


def report(region, country, confirmed, deaths, recovered):
    DayRecord = collections.namedtuple(
        'DayRecord',
        ['date',
         'active',
         'active_delta',
         'confirmed',
         'confirmed_delta',
         'deaths',
         'deaths_delta',
         'recovered',
         'recovered_delta'])
    start = datetime.date(2020, 1, 22)
    days_c = next(c for c in confirmed
                  if c[1] == country and c[0] == region)[4:]
    days_d = next(c for c in deaths
                  if c[1] == country and c[0] == region)[4:]
    days_r = next(c for c in recovered
                  if c[1] == country and c[0] == region)[4:]
    days = [(start+datetime.timedelta(days=day_num), tc, td, tr)
            for (day_num, tc, td, tr)
            in zip(range(len(days_c)), days_c, days_d, days_r)]

    for (today, previous) in ((d, d-1) for d in range(len(days))):
        if previous < 0:
            previous = 0
        today_date, tc, td, tr = days[today]
        _, pc, pd, pr = days[previous]
        active = int(tc)-(int(td)+int(tr))
        previous_active = int(pc)-(int(pd)+int(pr))
        yield DayRecord(
            date=today_date,
            active=active,
            active_delta=(active-previous_active),
            confirmed=int(tc),
            confirmed_delta=int(tc) - int(pc),
            deaths=td,
            deaths_delta=int(td)-int(pd),
            recovered=tr,
            recovered_delta=int(tr)-int(pr))


def printReport(region, country, days=10):
    reportData = list(report(region, country, confirmed, deaths, recovered))
    if days is None:
        days = len(reportData)
    print((f"{'Date':<10} "
           f"{'Active':>7} "
           f"{'(+/-)':>7} "
           f"{'Confirm':>7} "
           f"{'(+/-)':>7} "
           f"{'Deaths':>7} "
           f"{'(+/-)':>7} "
           f"{'Recover':>7} "
           f"{'(+/-)':>7}"))
    for (today, a, da, c, dc, d, dd, r, dr) in reportData[-days:]:
        print((f"{today} "
               f"{a:>7} "
               f"{da:>7} "
               f"{c:>7} "
               f"{dc:>7} "
               f"{d:>7} "
               f"{dd:>7} "
               f"{r:>7} "
               f"{dr:>7}"))

printReport('', 'South Africa')

