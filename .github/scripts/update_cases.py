from tableauscraper import TableauScraper as TS
from subprocess import run
from bs4 import BeautifulSoup
import urllib3
from datetime import datetime
import pandas as pd

init_url = "https://www.sandiegocounty.gov/content/sdc/hhsa/programs/phs/community_epidemiology/dc/human-monkeypox/localcases.html"
request = run( f"curl -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36' {init_url}", shell=True, capture_output=True, text=True )
soup = BeautifulSoup( request.stdout, "html.parser" )
iframe = soup.find( "div", {"class": "external parbase section"} ).find( "iframe" )
iframe_src = iframe.attrs["src"]
db_source = urllib3.util.parse_url( iframe_src ).path

ts = TS()
ts.loads( f"https:{db_source}" )
dashboard = ts.getWorkbook()
for i in dashboard.worksheets:
    if i.name == 'Cumulative Cases':
        cases = int( i.data.values[0][0] )
    elif i.name == 'Text2':
        date = i.data.iloc[0,0]
        date = datetime.strptime( date, "%m/%d/%Y" )

case_df = pd.read_csv( "MPX_cases.csv", parse_dates=["date"])

# if found date is greater than last date in cases database
if case_df.iloc[-1]["date"] < date:
    assert case_df.iloc[-1]["cases"] <= cases, f"New cases ({cases}) on {date} is less than the previous data ({case_df.iloc[-1]['date'].strftime('%Y-%m-%d')}: {case_df.iloc[-1]['cases']})"
    print( "New data has been found" )
    case_df = pd.concat( [case_df, pd.DataFrame({"date" : date, "cases" : cases }, index=[1])], ignore_index=True )
    case_df.to_csv( "MPX_cases.csv", index=False )
else:
    print( "No new data has been found" )
