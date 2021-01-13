-- create new schema
CREATE SCHEMA ausforecast;

-- create temp table to parse dates from text
DROP TABLE IF EXISTS raw_forecast;
CREATE TEMP TABLE raw_forecast (
  date TEXT,
  extended_text TEXT,
  fire_danger TEXT,
  forecast TEXT,
  icon_descriptor TEXT,
  issue TEXT,
  location TEXT,
  rain_max TEXT,
  rain_min TEXT,
  rain_prob TEXT,
  short_text TEXT,
  sunrise TEXT,
  sunset TEXT,
  temp_max TEXT,
  temp_min TEXT,
  uv_cat TEXT,
  uv_index TEXT
);
COPY raw_forecast FROM '/dataset_aus.csv'
-- The CSV data file has a string header which we need to ignore.
CSV HEADER
-- this NULL field defines what our null values will appear as.
NULL AS 'null';

-- Clear out existing schema if it exists and create dataset with date casts
-- Note: date case because python datetimes don't like 9999-xx-xx
DROP TABLE IF EXISTS ausforecast;
CREATE TABLE ausforecast AS
SELECT
  TO_DATE(date, 'YYYY-MM-DD') AS date,
  extended_text,
  fire_danger,
  forecast,
  icon_descriptor,
  TO_DATE(issue, 'YYYY-MM-DD') AS issue,
  location,
  rain_max,
  rain_min,
  rain_prob,
  short_text,
  sunrise,
  sunset,
  temp_max,
  temp_min,
  uv_cat,
  uv_index
FROM raw_forecast;