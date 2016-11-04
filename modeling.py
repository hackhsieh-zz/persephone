# Part 0: Libraries:
from sklearn.cross_validation import train_test_split
from sklearn.ensemble import GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.externals import joblib
import matplotlib.pyplot as plt
import statsmodels.api as sm
import pandas as pd
import numpy as np
import pickle


# Part 1: Functions:
# function 1:
def fit_model_sklearn(df, commodity, model_name):
    """
    INPUT: df (master dataframe); \
    commodity (the type of commodity that one whishes to predict); \
    mode_name (type of model)
    OUT: model (the fitted modle); X_train; X_test; y_train; y_test
    PURPOSE: fitting the model using sklearn
    """
    com_df = df[df['commodity_desc'] == commodity]
    y, X = com_df['value'], com_df.drop(
        ['commodity_desc', 'value'], axis=1
        )
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.33, random_state=42
        )

    if model_name == "Linear Regression":
        model = LinearRegression()
    elif model_name == 'RandomForestRegressor':
        model = RandomForestRegressor(n_estimators=50)
    elif model_name == 'ExtraTreesRegressor':
        model = ExtraTreesRegressor(n_estimators=50)
    elif model_name == 'GradientBoostingRegressor':
        params = {
            'n_estimators': 500, 'max_depth': 4,
            'min_samples_split': 1, 'learning_rate':
            0.01, 'loss': 'ls'
        }
        model = GradientBoostingRegressor(**params)
    model.fit(X_train, y_train)
    return model, X_train, X_test, y_train, y_test


# function 2:
def fit_model_sm(df, commodity, model_name):
    """
    INPUT: df (master dataframe); \
    commodity (the type of commodity that one whishes to predict); \
    mode_name (type of model)
    OUT: model (the fitted modle); X_train; X_test; y_train; y_test
    PURPOSE: fitting the model using 'stats model'
    """
    com_df = df[df["commodity_desc"] == commodity]
    y, X = com_df['value'], com_df.drop(
            ['commodity_desc', 'value'], axis=1
        )

    if model_name == "Linear Regression":
        X = sm.add_constant(X)
        X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.33, random_state=42
            )
        model = sm.OLS(y_train, X_train)

    results = model.fit()
    return model, results, X_train, X_test, y_train, y_test


# function 3:
def fit_all_commodities(df, commodities_list, model_name):
    """
    INPUT: df (dataframe), \
    commodity_list (list of respective commodities \
    for which one whishes to build regressio models)
    OUTPUT: print result; write pickled models to file path
    PURPOSE: fit all models at once
    """
    sklearn_models = {
        'RandomForestRegressor', 'ExtraTreesRegressor',
        'GradientBoostingRegressor'
    }
    sm_models = {"Linear Regression"}
    for commodity in commodities_list:
        if model_name in sklearn_models:
            model, X_train, X_test, y_train, y_test = \
                fit_model_sklearn(df, commodity, model_name)
            predict = model.predict(X_test)
            print "***********************"
            print "{}'s adjusted r^2 score with {} is:".format(
                    commodity, model_name
                )
            print r2_score(y_test, predict)
        elif model_name in sm_models:
            model, results, X_train, X_test, y_train, y_test = \
                fit_model_sm(df, commodity, model_name)
        # pickle model:
        joblib.dump(model, '{}_with_{}.pkl'.format(
            commodity, model_name)
        )


# Part 2: Main Code:
if __name__ == '__main__':
    """
    This file:
    1) combines the weather data frame and yield data frame
    2) Fits Linear Regression, RandomForestRegressor, ExtraTreesRegressor,\
    GradientBoostingRegressor for each of the commodities (ex. Corn, Barley).
    It also prints the results of the model with its cross validated \
    adjusted R^2 score, and pickles respective models.
    """
    # ________________________________
    # ________________________________
    # File process I: combines weather/yield data, reformat:
    # ________________________________
    # ________________________________
    # i. Loading yield data:
    yield_df = pd.read_csv(
            'target_states_yield.csv'
        )
    # a): Filtering out null values:
    yield_df = yield_df[yield_df["unit_desc"].notnull()]
    # b): Declaring columns:
    drop_columns = [
        'Unnamed: 0', 'data_item', 'state_alpha', 'statisticcat_desc',
        'asd_code', 'asd_desc', 'congr_district_code', 'county_ansi',
        'county_code', 'location_desc'
    ]
    # c): Drop unneeded columsn for yield/acre prediction:
    yield_df.sort("year", ascending=True, inplace=True)
    yield_df.drop(drop_columns, axis=1, inplace=True)
    yield_df.reset_index(inplace=True)
    # d): Create dummy variables:
    yield_df = pd.get_dummies(
            yield_df, columns=['prodn_practice_desc', 'util_practice_desc'],
            drop_first=True
        )
    # e): Drop variables that have already been dummified:
    yield_df.drop('class_desc', axis=1, inplace=True)
    # f): Generate commedity list
    # (these will be the commodities we will be fitting:
    commodities_list = list(yield_df['commodity_desc'].unique())
    # ________________________________
    # iii. Loading weather data:
    weather_df = pd.read_csv(
            'cleaned_master_weather_complete.csv'
        )
    # a): Declaring variables:
    features = [
        'CLDD', 'DPNP', 'DPNT', 'HTDD', 'DT90', 'DX32', 'DT00',
        'DT32', 'DP01', 'DP05', 'DP10', 'MMXP', 'MMNP', 'TEVP',
        'HO51A0', 'HO51P0', 'HO52A0', 'HO52P0', 'HO53A0', 'HO53P0',
        'HO54A0', 'HO54P0', 'HO55A0', 'HO55P0', 'HO56A0', 'HO56P0',
        'HO01A0', 'HO03A0', 'LO51A0', 'LO51P0', 'LO52A0', 'LO52P0',
        'LO53A0', 'LO53P0', 'LO54A0', 'LO54P0', 'LO55A0', 'LO55P0',
        'LO56A0', 'LO56P0', 'LO01A0', 'LO03A0', 'MO51A0', 'MO51P0',
        'MO52A0', 'MO52P0', 'MO53A0', 'MO53P0', 'MO54A0', 'MO54P0',
        'MO55A0', 'MO55P0', 'MO56A0', 'MO56P0', 'MO01A0', 'MO03A0',
        'EMXP', 'MXSD', 'DSNW', 'TPCP', 'TSNW', 'EMXT', 'EMNT',
        'MMXT', 'MMNT', 'MNTM', 'TWND'
    ]
    # b): Drop unneeded columns:
    weather_df.drop(
            ['Unnamed: 0', 'LATITUDE', 'LONGITUDE'], axis=1, inplace=True
        )
    # c): Grab monthly value:
    weather_df["MONTH"] = weather_df["DATE"].apply(lambda x: int(str(x)[4:6]))
    # d): Turn -9999.00 (the way the data record Nan values) into Nan values:
    for feature in features:
        weather_df[feature] = weather_df[feature].apply(
                lambda x: np.nan if (x == -9999.00) else (x)
            )
    # e): Filter out a row where COUNTY value is missing:
    weather_df = weather_df[weather_df["COUNTY"].notnull()]
    # f): Average annual weather day:
    weather_df = \
        weather_df.groupby(['STATE', 'COUNTY', 'YEAR']).mean().reset_index()
    weather_df.drop(['MONTH'], axis=1, inplace=True)
    # g): Drop columns with more 30% na values:
    drop_features = []
    for c in weather_df:
        if np.mean(pd.isnull(weather_df[c])) > 0.3:
            drop_features.append(c)

    weather_df.drop(drop_features, axis=1, inplace=True)
    # h): fill na:
    # since the df is order based on time and location \
    # this will fill the na with the values of next year.
    weather_df.fillna(method="bfill", inplace=True)
    # ________________________________
    # v. Combining dataframes:
    # a): Merge dfs (SQL style joins):
    model_df = pd.merge(
        left=yield_model_df, right=weather_model_df,
        left_on=['state_name', 'county_name', 'year'],
        right_on=['STATE', 'COUNTY', 'YEAR'], how="inner"
    )
    model_df.drop(
            ['Unnamed: 0_x', 'Unnamed: 0_y', 'unit_desc'], axis=1, inplace=True
        )
    # b): Grouping column names:
    categorical_features = ['state_name', 'county_name']
    dependent_variable = ['value']
    # c): Get dummy variables for categorical variables:
    model_df = pd.get_dummies(
            model_df, columns=categorical_features, drop_first=True
        )
    # After cleanning, some commodities has no values \
    # d): Removing these commodities:
    commodities_list.remove('SAFFLOWER')
    commodities_list.remove('MUSTARD')
    commodities_list.remove('LENTILS')
    commodities_list.remove('PEAS')
    # ________________________________
    # ________________________________
    # File process II: Modeling:
    # ________________________________
    # ________________________________
    models = [
        'RandomForestRegressor', 'Linear Regression'
        'ExtraTreesRegressor', 'GradientBoostingRegressor'
    ]
    for model in models:
        fit_all_commodities(model_df, commodities_list, model)
