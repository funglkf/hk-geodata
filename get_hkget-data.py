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

## Get DatasetInfo data to Json object
for script in script_list:
  if 'var g_gsDatasetInfo' in str(script):
    # print(str(script))
    m = re.search(r'var g_gsDatasetInfo = (.+?);', str(script), re.DOTALL)
    open('docs/g_gsDatasetInfo.json', 'a').write(m.group(1))
    g_gsDatasetInfo_json = json.loads(m.group(1))

  if 'var g_hkgsCategoryInfo' in str(script):
    m = re.search(r'var g_hkgsCategoryInfo = (.+?);', str(script), re.DOTALL)
    open('docs/g_hkgsCategoryInfo.json', 'a').write(m.group(1))
    g_hkgsCategoryInfo_json = json.loads(m.group(1))

  if 'var hkgsDataProviderList' in str(script):
    m = re.search(r'var hkgsDataProviderList = (\[.+?\])', str(script), re.DOTALL)
    open('docs/hkgsDataProviderList.json', 'a').write(m.group(1))
    hkgsDataProviderList_json = json.loads(m.group(1))

  if 'var hkgsDataProviderAndDatasetMapping' in str(script):
    m = re.search(r'var hkgsDataProviderAndDatasetMapping = ({.+?})', str(script), re.DOTALL)
    open('docs/hkgsDataProviderAndDatasetMapping.json', 'a').write(m.group(1))
    hkgsDataProviderAndDatasetMapping_json = json.loads(m.group(1))

  if 'var hkgsCategoryList' in str(script):
    m = re.search(r'var hkgsCategoryList = (.+?);', str(script), re.DOTALL)
    open('docs/hkgsCategoryList.json', 'a').write(m.group(1))
    hkgsCategoryList_json = json.loads(m.group(1))


## Changing Json object to DataFrame
df_g_gsDatasetInfo = pd.DataFrame.from_records(g_gsDatasetInfo_json)
df_hkgsDataProviderList = pd.DataFrame.from_records(hkgsDataProviderList_json)
df_hkgsCategoryList= pd.DataFrame.from_records(hkgsCategoryList_json)
# df_hkgsDataProviderAndDatasetMapping = pd.DataFrame.from_records(hkgsDataProviderAndDatasetMapping_json)
# df_g_hkgsCategoryInfo = pd.DataFrame.from_records(g_hkgsCategoryInfo_json)


## Mapping Provider Name
df_maindata = pd.merge(df_g_gsDatasetInfo[['DATASET_UUID','DATASET_NAME_EN','DATASET_NAME_TC','DATA_PROVIDER_ID']],
         df_hkgsDataProviderList[['dpid','nameEN','nameTC']], left_on='DATA_PROVIDER_ID', right_on='dpid').drop(columns=['dpid', 'DATA_PROVIDER_ID'])

## write to index page
with open('docs/index.html', 'w') as fo:
    df_maindata.to_html(fo)