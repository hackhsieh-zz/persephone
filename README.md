# __persephone__
* A data science project: crop yield forecasting model

* I: Motivation:
  * Potential global food security crisis
  * Reasons:
    * Skyrocketing world population (+2.3 billion by 2050 based on U.N. study)
      * Source: http://www.un.org/en/development/desa/news/population/2015-report.html
    * Shrinking arable land/person:
      * 0.38 hector (year: 1970)
      * 0.23 hector (year: 2000)
      * 0.15 hector (year: 2050; projected)
    * Extreme climate --> new normal

* II: Task:
  * Can we quantify the impact of global warming to crop yield lost?
  * Example:
    * If the global average temperature increase by 2 celsius (target of United Nations Climate Change Conference in Paris), what will happen to crop yield ?
    * Source: http://www.npr.org/sections/thetwo-way/2015/12/12/459502597/2-degrees-100-billion-the-world-climate-agreement-by-the-numbers

* III: Method:
  * Regression with historical record
  * Took advantage of U.S.'s rich microclimates
  * Data:
    * Historical data
    * Weather data from NOAA (National Oceanic and Atmospheric Administration)
      * Source: https://www.ncdc.noaa.gov/cdo-web/
    * Field crop yield data from USDA (U.S. Department of Agriculture)
      * Source: https://www.nass.usda.gov/Quick_Stats/
    * Link by location/time (county/year)
  * Focused on top 10 agriculture states (responsible for 50% of agriculture economic output)
  * Field crops (rotational crop): ex. corn, wheat, barley
  * Time: 1960 - 2014 (Start at 1960 because that is approximately when modern farming takes place)

* IV: Models:
  * 18 models for respective field crops
  * Linear Regression
  * Random Forest Regression:
    * Adjusted R squared score (wheat): 93 %
    * Adjusted R squared score (corn): 90 %
    * Adjusted R squared score (cotton): 81 %

* V: Result: Features Importance:
  * Feature 1
  * Feature 2
  * Feature 3
  * Feature 4

* VI: Result: Feature #1 (for corn):
  * +1 unit --> % yield/acre change

* VII: Result: Feature #2 (for corn):
  * +1 unit -->  % yield/acre change

* VIII: Result: Prediction:
  * At +2 celsius --> economic lost $xxx USD/yield

* IX: Future:
  * Model on all 50 states of U.S.
  * Model with more complete  weather data
  * Model on other crops
  * Crop recommender
