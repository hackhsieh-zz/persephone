# Part 0: Libraries:
from collections import OrderedDict
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np


# Part 1: Functions:
# function 1:
def parse_data_item(s):
    """
    INPUT: s (string; description of data value)
    OUTPUT: attributes (set of strings; sub-domain \
        /yield-type/season-harvested etc.) \
        unit (string; ex. BU/net harvested acre)
    OVERVIEW: Parse String in column "Data Item":
    """
    left, unit = s.split(" - YIELD, MEASURED IN ")
    attributes = set(left.split(", ")[1:])
    master_attributes.update(attributes)
    return attributes, unit


# function 2:
def add_columns(df, s):
    """
    INPUT: df (data frame), s (set of strings of column names )
    OUTPUT: N/A
    OVERVIEW: Add new columns to dataframe:
    """
    for name in s:
        df[name] = \
            df["Crop Attributes"].apply(lambda x: 1 if (name in x) else 0)


# function 3:
def count_irrigation(df, time_period):
    """
    INPUT: df (data frame), time_period \
        (string; the time period this calculation is based on)
    OUTPUT: N/A
    OVERVIEW: count/print of irrigated vs. non-irrigated crops:
    """
    irrigated = len(df[df["IRRIGATED"] == 1])
    non_irrigated = len(df[df["NON-IRRIGATED"] == 0])
    print "__Time period: {}__".format(time_period)
    print "Total irrigated crops: {}".format(irrigated)
    print "Total non-irrigated crops: {}".format(non_irrigated)
    print "Ratio of irrigated/non-irrigated: {}".format(
        irrigated/float(non_irrigated)
    )


# function 4:
def count_sub_type(df, time_period):
    """
    INPUT: df (data frame), time_period \
        (string; the time period this calculation is based on)
    OUTPUT: count (# of total sub_types of all \
        commodities in this data frame)
    OVERVIEW: count/print total sub_type of master commodity during a period:
    """
    df = df[df["year"] == time_period]
    all_commodities = df["commodity_desc"].unique()
    total_commodities, total_sub_domains = len(all_commodities), 0
    print "__Time period:{}__".format(time_period)
    for commodity in all_commodities:
        sub_domains_count = len(df[df["commodity_desc"] == commodity])
        total_sub_domains += sub_domains_count
        print "{} has {} sub_types".format(commodity, sub_domains_count)
    print "Total general commodities: {}".format(total_commodities)
    print "Total commodities: {}".format(total_sub_domains)


# function 5:
def convert_unit(x, conversion_dict):
    """
    INPUT: x (row of dataframe); conversion_dict \
        (dict; unit conversion (key = "commodity; value = conversion rate))
    OUPUT: new_val (float)
    OVERVIEW: N/A
    """
    new_val = x['value']
    if "BU" in x['unit_desc']:
        new_val = round(new_val*conversion_dict[x['commodity_desc']], 2)
    return new_val


# function 6:
def change_unit_name(x):
    """
    INPUT: x (row of dataframe)
    OUPUT: new_name (str)
    OVERVIEW: N/A
    """
    new_name = x['unit_desc']
    if "BU" in x['unit_desc']:
        new_name = x['unit_desc'].replace('BU', 'TONS')
    return new_name


# function 7:
def standardrize_unit(df, conversion_dict):
    """
    INPUT: df(data frame), conversion_dict \
        (dict; unit conversion (key = "commodity; value = conversion rate))
    OUTPUT: df(data frame)
    OVERVIEW: standardrize data frame unit to ton/area
    """
    df['value'] = df.apply(convert_unit, axis=1, args=(conversion_dict,))
    df['unit_desc'] = df.apply(change_unit_name, axis=1)
    return df


# function 8:
def find_BU_commdity(df):
    """
    INPUT: df (dataframe)
    OUTPUT: BU_commidty (list of unique commodity that uses BU as unit)
    """
    return list(df[df['unit_desc'].apply(
        lambda x: True if 'BU' in x else False)]['commodity_desc'].unique()
    )


# Part 2: Main Code:
if __name__ == '__main__':
    """
    This file cleans and reformat the yield data.

    Descriptions of features:

    # asd_code: NASS defined county groups, \
    # unique within a state,2-digit ag statistics district code
    # asd_desc: Ag statistics district name
    # class_desc: Generally a physical attribute \
    # (e.g., variety, size, color, gender) of the commodity.
    # congr_district_code: US Congressional District 2-digit code.
    # location_desc: full description for the location dimension.
    # prodn_practice_desc: A method of production or action \
    # taken on the commodity (e.g., IRRIGATED, ORGANIC, ON FEED)
    # util_practice_desc: Utilizations (e.g., GRAIN, FROZEN, SLAUGHTER) \
    # or marketing channels (e.g., FRESH MARKET,PROCESSING, RETAIL).

    # commodity_desc: The primary subject of interest \
    # (e.g., CORN, CATTLE, LABOR, TRACTORS, OPERATORS).
    # data_item: A concatenation of six columns: commodity_desc, \
    # class_desc, prodn_practice_desc, util_practice_desc,statisticcat_desc, \
    # and unit_desc.
    # state_alpha: State abbreviation, 2-character alpha code
    # statisticcat_desc: The aspect of a commodity being measured \
    # (e.g., AREA HARVESTED, PRICE RECEIVED, INVENTORY, SALES).
    # unit_desc: The unit associated with the statistic category \
    # (e.g.ACRES, $ / LB, HEAD, $, OPERATIONS).
    # value: Published data value or suppression reason code.
    # year: The numeric year of the data
    """
    # i. Declaring Variables:
    start_year, end_year = 1970, 2014
    master_attributes = set()
    # These are the years where yield data is missing (noticed from EDA)
    missing_yield_years = [1982, 1984, 1985]
    # Targeting 10 top agriculture states (based on economic output)
    # Source: http://www.ers.usda.gov/faqs.aspx (top 10 agriculture states)
    targest_states = [
        "California", "Iowa", "Texas", "Nebraska", "Illinois",
        "Minnesota", "Kansas", "Indiana", "North Carolina", "Wisconsin"
    ]
    # Dataframe to hold all info:
    yield_master_df = pd.DataFrame()
    targest_states = [state.upper() for state in targest_states]
    # ________________________________
    # ii. Load csvs: Load csv files and combine them into master dataframe:
    for year in xrange(start_year, end_year+1):
        if year not in missing_yield_years:
            year_df = pd.read_csv(
                "/Data/yield_{}.csv".format(year)
            )
            yield_master_df = yield_master_df.append([year_df])
    # ________________________________
    # iii: Reordering master_df:
    yield_master_df.sort("year", ascending=True, inplace=True)
    yield_master_df.reset_index(inplace=True)
    # ________________________________
    # iv: Refine dataframe:
    excess_columns = [
        'index', 'Unnamed: 0', 'CV', 'agg_level_desc', 'begin_code',
        'country_code', 'country_name', 'domain_desc',
        'domaincat_desc', 'end_code', 'freq_desc', 'group_desc',
        'load_time', 'reference_period_desc', 'reference_period_desc',
        'region_desc', 'sector_desc', 'source_desc', 'state_ansi',
        'state_fips_code', 'state_alpha', 'watershed_code', 'watershed_desc',
        'zip_5'
    ]
    key_columns = [
        'commodity_desc', 'county_name', 'data_item', 'state_alpha',
        'state_name', 'statisticcat_desc',
        'unit_desc', 'value', 'year'
    ]
    other_columns = [
        'asd_code', 'asd_desc', 'class_desc', 'congr_district_code',
        'location_desc', 'prodn_practice_desc',
        'util_practice_desc', 'county_ansi', 'county_code'
    ]
    # Filter out unnecessary columns:
    yield_model_df = \
        yield_master_df.filter(key_columns+other_columns, axis=1)
    # Filter unnecessary values:
    yield_model_df = \
        yield_model_df[
            yield_model_df['county_name'] != 'OTHER (COMBINED) COUNTIES'
        ]
    # Convert values in column "Unit" to float:
    yield_model_df["value"] = \
        yield_model_df["value"].apply(lambda x: float(x.replace(",", "")))
    # ________________________________
    # v: Feature engineering / unit conversions:

    # a): Creating conversion rates for diff units (for crops measured in bu):
    # resources:
    # https://www.agric.gov.ab.ca/app19/calc/crop/bushel2tonne.jsp
    # http://www.grains.org/buyingselling/conversion-factors
    tonne_per_ton = 0.907185
    # tonne_per_bu for each commodities:
    tonne_bu_dict = OrderedDict(
        {
            "CORN": 0.25, "BARLEY": 0.021, "WHEAT": 0.027,
            "SORGHUM": 0.25, "OATS": 0.015, 'RYE': 0.025,
            "SOYBEANS": 0.027, "FLAXSEED": 0.025
        }
    )
    # ton_per_bu for each commodities:
    ton_bu_dict = {}
    for commodity in tonne_bu_dict:
        ton_bu_dict[commodity] = tonne_bu_dict[commodity]/tonne_per_ton

    # b): standardized df unit to 'TONS / ACRE':
    yield_model_df = standardrize_unit(yield_model_df, ton_bu_dict)
    # c): filter out the unit we are looking for (yield/acre):
    yield_model_df = ['TONS / ACRE', 'LB / ACRE']
    yield_model_df = \
        yield_model_df[
            yield_model_df['unit_desc'].apply(
                lambda x: True if x in target_units else False
            )
        ]
    # d): filtering out df with 10 target states:
    yield_model_df = \
        yield_model_df[
            yield_model_df['state_name'].apply(
                lambda x: True if (x in targest_states) else False
            )
        ]
    # e): write dataframe into new csv file:
    yield_model_df.to_csv(
        'target_states_yield.csv'
    )
