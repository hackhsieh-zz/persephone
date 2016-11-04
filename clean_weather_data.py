# Part 0: Libraries:
from collections import OrderedDict
import shapefile
import geopandas as gpd
import pandas as pd
import numpy as np
import requests
import us
import json
import re


# Part 1: Functions:
# function #1:
def get_county(row):
    """
    INPUT: row (series; row of data)
    OUTPUT: county (str), state (str)
    OVERVIEW: FROM FCC
    """
    lat, lon = row['LATITUDE'], row['LONGITUDE']
    loc_point = gpd.geoseries.Point(lon, lat)
    return loc_point


# function #2:
def generates_county_into(state_alphabets):
    """"
    INPUT: state_alphabets(str; abbreviation of states)
    OUTPUT: the county information of the state
    """"
    return us.states.lookup(state_alphabets).shapefile_urls('county')


# Part 2: Main Code:
if __name__ == '__main__':
    """
    This file cleans and formats the weather data.
    In particular, it uses geopandas to convert latitude and longitude \
    informations to its corresponding counties using a US country shape file.
    """
    # i: Declaring Variables:
    start_year, end_year = 1970, 2014
    # Excluding the years where the yield data is missing:
    missing_yield_years = [1982, 1984, 1985]
    # Targeting 10 top agriculture states (based on economic output)
    # Source: http://www.ers.usda.gov/faqs.aspx (top 10 agriculture states)
    target_states_lower = [
        "California", "Iowa", "Texas", "Nebraska", "Illinois",
        "Minnesota", "Kansas", "Indiana", "North Carolina", "Wisconsin"
    ]
    target_states_upper = [state.upper() for state in target_states_lower]
    weather_master_df = pd.DataFrame()
    # Dict of all the maximum number of files a state have on weather:
    weather_data_dict = {
        'California': 16, 'Iowa': 5, 'Texas': 16, 'Nebraska': 6, 'Illinois': 6,
        'Minnesota': 5, 'Kansas': 6, 'Indiana': 6, 'North Carolina': 5,
        'Wisconsin': 4
    }
    # state alphabets abbreviations:
    state_alphabet = [
        'NC', 'NE', 'TX', 'MN', 'IN', 'WI', 'IA', 'KS', 'IL', 'CA'
    ]
    # ________________________________
    # ii: Load csv files and combine them into master dataframe:
    for state in target_states_lower:
        state_lower = state.lower()
        for file_num in xrange(1, weather_data_dict[state]+1):
            filename = 'weather_{state}_{file_num}.csv'.format(
                state=state_lower, file_num=file_num
            )
            year_df = pd.read_csv(
                "/Users/Hsieh/Desktop/persephone/Data/WeatherComplete/" +
                "{state}/{filename}".format(state=state, filename=filename)
            )
            weather_master_df = weather_master_df.append([year_df])
    # ________________________________
    # iii: Refine dataframe:
    # a): Reordering master_df:
    weather_master_df.reset_index(inplace=True)
    # b): Declare lists of columns type:
    excess_columns = [
        "Unnamed: 0", "index", 'Measurement Flag', "Measurement Flag.1",
        "Measurement Flag.2", "Measurement Flag.3", "Measurement Flag.4",
        "Measurement Flag.5", "Measurement Flag.6", "Measurement Flag.7",
        "Measurement Flag.8", "Measurement Flag.9", "Number of Days",
        "Number of Days.1", "Number of Days.2", "Number of Days.3",
        "Number of Days.4", "Number of Days.5", "Number of Days.6",
        "Number of Days.7", "Number of Days.8", "Number of Days.9",
        "Quality Flag", "Quality Flag.1", "Quality Flag.2", "Quality Flag.3",
        "Quality Flag.4", "Quality Flag.5", "Quality Flag.6", "Quality Flag.7",
        "Quality Flag.8", "Quality Flag.9", "Units", 'Units.1',
        "Units.2", "Units.3", "Units.4", "Units.5", "Units.6",
        "Units.7", "Units.8", "Units.9"
    ]
    other_columns = ['ELEVATION', 'STATION', 'STATION_NAME']
    key_columns = ['DATE', 'LATITUDE', 'LONGITUDE']
    feature_columns = [
        'CLDD', 'DPNP', 'DPNT', 'HTDD', 'DT90', 'DX32',
        'DT00', 'DT32', 'DP01', 'DP05', 'DP10', 'MMXP',
        'MMNP', 'TEVP', 'HO51A0', 'HO51P0', 'HO52A0',
        'HO52P0', 'HO53A0', 'HO53P0', 'HO54A0', 'HO54P0',
        'HO55A0', 'HO55P0', 'HO56A0', 'HO56P0', 'HO01A0',
        'HO03A0', 'LO51A0', 'LO51P0', 'LO52A0', 'LO52P0',
        'LO53A0', 'LO53P0', 'LO54A0', 'LO54P0', 'LO55A0',
        'LO55P0', 'LO56A0', 'LO56P0', 'LO01A0', 'LO03A0',
        'MO51A0', 'MO51P0', 'MO52A0', 'MO52P0', 'MO53A0',
        'MO53P0', 'MO54A0', 'MO54P0', 'MO55A0',
        'MO55P0', 'MO56A0', 'MO56P0', 'MO01A0', 'MO03A0',
        'EMXP', 'MXSD', 'DSNW', 'TPCP', 'TSNW', 'EMXT',
        'EMNT', 'MMXT', 'MMNT', 'MNTM', 'TWND'
    ]
    # c): filter out unnecessary columns:
    weather_model_df = weather_master_df.filter(
        key_columns+feature_columns, axis=1
    )
    # d): Add year column:
    weather_model_df['YEAR'] = weather_model_df['DATE'].apply(
        lambda x: int(str(x)[0:4])
    )
    # ________________________________
    # iv: clean dataframe:
    weather_model_df = weather_model_df[
        weather_model_df["LATITUDE"] != "unknown"
    ]
    weather_model_df = weather_model_df[
        weather_model_df["LONGITUDE"] != "unknown"
    ]
    weather_model_df = weather_model_df[
        weather_model_df["LONGITUDE"].notnull()
    ]
    weather_model_df['LATITUDE'] = weather_model_df['LATITUDE'].apply(
        lambda x: float(x)
    )
    weather_model_df['LONGITUDE'] = weather_model_df['LONGITUDE'].apply(
        lambda x: float(x)
    )
    # ________________________________
    # v: map latitude, longtitude to county:
    gpd_file = gpd.read_file(
        "/Users/Hsieh/Desktop/persephone/Data/uscounties.geojson"
    )
    geo_series = weather_model_df.apply(get_county, axis=1)
    gpd_df = gpd.GeoDataFrame(geometry=geo_series)
    counties_df = gpd.sjoin(gpd_df, gpd_file, op="within")
    weather_model_df['COUNTY'] = counties_df['name']
    weather_model_df['STATE'] = counties_df['state_name']
    # vi: write cleaned df to csv file:
    weather_model_df.to_csv(
        'cleaned_master_weather_complete.csv'
    )
