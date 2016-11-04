# Part 0: Libraries:
import requests
import json
import csv
import urllib2
import pandas as pd


# Part 1: Functions:
# function 1: grab file with url and write to json file:
def data_from_url(url, filename, data_category):
    r = requests.get(url)
    print r
    with open('Data/{}/{}.json'.format(data_category, filename), 'w') as f:
        json.dump(r.json(), f)


# function 2: read json file into pd data frame:
def json_to_df(filename, data_category):
    with open('Data/{}/{}'.format(data_category, filename)) as f:
        data = json.load(f)
    return pd.DataFrame.from_dict(data['data'])


# function 3: generate yield data in csv by year:
def generate_yield_data(year, data_category):
    yearly_url = \
        "http://nass-api.azurewebsites.net/api/api_get?source_desc" + \
        "=SURVEY&agg_level_desc=COUNTY&sector_desc=CROPS&group_desc" + \
        "=FIELD%20CROPS&year={}&freq_desc=ANNUAL".format(year)

    try:
        print "this is year: {}".format(year)
        data_from_url(yearly_url, "yield_{}".format(year), data_category)
    except:
        print "{} doesn't work!!!!!".format(year)
        yield_bad_years.append(year)
        return
    yield_df = json_to_df("Data/{}/yield_{}.json".format(data_category, year))
    yield_df.to_csv("Data/{}/yield_{}.csv".format(data_category, year))


# Part 2: Main Code:
if __name__ == '__main__':
    '''
    This file grabs the crop yield data from the nass-api.
    The source of data is from the USDA.

    # Descriptions of yield data:
    # Respective aggregated annual field crops yields on county level (U.S.) \
    # from 1970 to 2014. For this project, we will be \
    # focusing on the 10 top agriculture states, interms of total \
    # agricultural economic output, which are responsible for 50% \
    # of the total U.S. agricultural economic activities. \
    # This data was collected via USDA annual agriculture survey. \
    # Link: http://innovationchallenge.azurewebsites.net/#NassTab
    '''
    # Declaring variables:
    data_category = "Yield"
    start_year, end_year = 1970, 2014
    yield_bad_years = [1982, 1984, 1985]

    # Generate yield data in csv form year by year from 1970 to 2014:
    for year in yield_bad_years:
        generate_yield_data(year, data_category)
