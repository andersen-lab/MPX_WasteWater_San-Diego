import urllib3
from lxml import etree, html
import re
from datetime import datetime
import pandas as pd

http = urllib3.PoolManager()
request = http.request( "GET", "https://www.sandiegocounty.gov/content/sdc/hhsa/programs/phs/community_epidemiology/dc/human-monkeypox/localcases.html")

assert request.status == 200, f"Request was unsuccessful. Status {request.status} returned."
parsed_data = html.fromstring( request.data )

cases = parsed_data.xpath('//*[@id="content-secondary"]/div[2]/div[7]/table/tbody/tr[2]/td[2]/b')[0].text
assert cases.isnumeric(), "Parsed string ('{cases}') is not numeric"
cases = int( cases )

date_str = parsed_data.xpath( '//*[@id="content-secondary"]/div[2]/div[6]' )[0].text_content()
date = re.search( '\d{1,2}\/\d{1,2}\/\d{4}', date_str )
assert date is not None, f"No date found in the following string: {date_str}"

date = date.group(0)
date = datetime.strptime( date, "%m/%d/%Y" )

case_df = pd.read_csv( "MPX_cases.csv", parse_dates=["date"])

# if found date is greater than last date in cases database
if case_df.iloc[-1]["date"] < date:
    assert case_df.iloc[-1]["cases"] < cases, f"New cases ({cases}) is less than the previous data ({case_df.iloc[-1]['date']})"
    print( "New data has been found" )
    case_df = pd.concat( [case_df, pd.DataFrame({"date" : date, "cases" : cases }, index=[1])], ignore_index=True )
    case_df.to_csv( "MPX_cases.csv", index=False )
else:
    print( "No new data has been found" )
