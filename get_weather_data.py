# Part 0: Libraries:
import requests
import json
import csv
import urllib2
import pandas as pd


# Part 1: Functions:
# function 1:
def generate_counties_df(state_name):
    """
    INPUT: state_name (str, name of the state)
    OUTPUT: counties_df (df that has columns of county name,
        state name, and respective FIPS ID)
    OVERVIEW: generating counties and their
        corresbonding location ids (FIPS) in pd form
    """
    column_names = ['Name', 'ID']
    counties_df = pd.read_csv(
        "Data/Weather/Locations/" +
        "{}_counties.txt".format(state_name), names=column_names
    )

    counties_df["State"] = [ID.split("(")[0] for ID in counties_df["ID"]]
    # remove ")" from end of the string:
    counties_df["ID"] = counties_df["ID"].apply(lambda x: x.replace(")", ""))
    # FIPS ID is the ID of the NOAA weather station
    # associated with respective counties:
    counties_df["FIPS ID"] = [ID.split("FIPS:")[1] for ID in counties_df["ID"]]
    # capitalized county name:
    counties_df["County"] = [
        name.split(" County")[0].upper()
        for name in counties_df["Name"]
    ]
    # dropping unnecessary columns:
    counties_df.drop(column_names, axis=1, inplace=True)
    return counties_df


# function 2:
def data_from_url(url, filename, data_category, token):
    """
    INPUT: url (str), filename (str), data_category (str), token (str)
    OUTPUT: N/A (no return but generates json file)
    OVERVIEW: grab file with url and write to json file (for weather data)
    """
    headers = {"token": token}
    r = requests.get(url, headers=headers)
    print r
    with open('Data/{}/{}.json'.format(data_category, filename), 'w') as f:
        json.dump(r.json(), f)


# function 3:
def json_to_df(filename, data_category):
    """
    INPUT: filename (str), data_category (str)
    OUTPUT: df (dataframe)
    OVERVIEW: read json file into pd data frame (weather)
    """
    with open('Data/{}/{}'.format(data_category, filename)) as f:
        data = json.load(f)
    df = pd.DataFrame.from_dict(data["results"])
    return df


# function 4:
def generate_yield_data(county_id, county_name, start_year, end_year):
    """
    INPUT: county_id (str), county_name (str), start_year (int), end_year(int)
    OUTPUT: N/A (no return but generates csv file)
    OVERVIEW: generates weather data in csv form year by year
    """
    locationid = master_locationid.format(county_id)
    filename = master_filename.format(start_year, end_year, county_name)
    startdate, enddate = master_startdate.format(start_year), \
        master_enddate.format(end_year)
    yearly_url = master_url.format(
        datasetid=datasetid,
        locationid=locationid, startdate=startdate, enddate=enddate
    )

    try:
        print "STARTS"
        print yearly_url
        data_from_url(yearly_url, filename, data_category, weather_token)
    except:
        print "THIS DOESN'T WORK!!!!!"
        return
    weather_df = json_to_df("{}.json".format(filename), data_category)
    weather_df.to_csv("Data/{}/{}.csv".format(data_category, filename))


# Part 2: Main Code:
if __name__ == '__main__':
    """
    This file grabs the weather data from the NOAA api.

    #Descriptions of weather data:

    # Historical weather (precipitation/air temperature)
    # data (1970~2014) of top 10 agriculture states from NOAA.

    # features:
    # EMXP (Extreme maximum daily precipitation)
    # MXSD (Maximum snow depth)
    # DSNW (Number days with snow depth > 1 inch)
    # TPCP (Total precipitation)
    # TSNW (Total snow fall)
    # EMXT (Extreme maximum daily temperature)
    # EMNT (Extreme minimum daily temperature)
    # MMXT (Monthly mean maximum temperature)
    # MMNT (Montly mean minimum temperature)
    # MNTM (Monthly mean temperature)
    """
    # i: Declaring Variables:
    # Targeting 10 top agriculture states (based on economic output)
    # Source: http://www.ers.usda.gov/faqs.aspx (top 10 agriculture states)
    target_states = [
        "California", "Iowa", "Texas", "Nebraska", "Illinois",
        "Minnesota", "Kansas", "Indiana", "North Carolina", "Wisconsin"
    ]
    target_states = [state.upper() for state in target_states]
    # the type of weather data grabbing from NOAA.
    datatype_key = [
        'EMXP', 'MXSD', 'DSNW', 'TPCP', 'TSNW',
        'EMXT', 'EMNT', 'MMXT', 'MMNT', 'MNTM'
    ]
    # ________________________________
    # ii: Declaring master vriables for grabbing data from API:
    # a): Master variables:
    master_filename, data_category = "weather_{}-{}_{}", "Weather"
    start_year, end_year = 1960, 1960
    weather_token = "lPtLBRYazwyqSgrWteXkaHStbdlWzqvV"
    # b): Variable: DataSet:
    # description: "Annual Summaries"
    datasetid = "ANNUAL"
    # c): Variable: Locations:
    master_locationid = "FIPS:{}"
    # d): Time frame:
    master_startdate, master_enddate = "{}-01-01", "{}-12-31"
    # e): Masater url:
    master_url = \
        "http://www.ncdc.noaa.gov/cdo-web/api/v2/data?" + \
        "datasetid={datasetid}&" + "datatypeid=TPCP&TS" + \
        "NW&EMXT&EMNT&MNTM&locationid={locationid}&" + \
        "startdate={startdate}&enddate={enddate}&unit" + \
        "s=metric&limit=1000"
    # ________________________________
    # iii. Generates Weather Data:
    for state in target_states:
        state_counties_df = generate_counties_df(state)
        for ID in state_counties_df["FIPS ID"]:
            generate_yield_data(ID, state, start_year, end_year)
