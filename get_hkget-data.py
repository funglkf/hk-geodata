from requests_html import HTMLSession
from bs4 import BeautifulSoup
import json
import re
import pandas as pd 

## Fetch the html file
session = HTMLSession()
response = session.get('https://geodata.gov.hk/gs/geodataQueryAPI-datasets')
# print(response.text)

## Parse the html file
soup = BeautifulSoup(response.text, 'html.parser')
# print(soup.title)

## Format the parsed html file
# strhtm = soup.prettify()

## Find all script content
script_list = soup.find_all('script')

## Get g_gsDatasetInfo data to Json object
for script in script_list:
  if 'var g_gsDatasetInfo' in str(script):
    
    m = re.search(r'var g_gsDatasetInfo = (.+?);', str(script), re.DOTALL)
    m.group(1)
    json_data = json.loads(m.group(1))

df_item = pd.DataFrame.from_records(json_data)


## write to index page
with open('docs/index.html', 'w') as fo:
    df_item.to_html(fo)