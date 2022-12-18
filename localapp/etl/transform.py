import pandas as pd
import logging


log = logging.getLogger()


def clean_string_field(data, regex_pattern, replace_string):
    '''Replace chars matching regex_pattern in data with replace_string'''
    clean_data = data.str.replace(regex_pattern, replace_string, regex=True)
    return clean_data

def split_string_column(input_df, msg_field, msg_content_header):
    '''Split coma separated string field from dataframe into separate df'''
    col_df = pd.DataFrame(input_df[msg_field].str.split(pat=',', expand=True))
    col_df.columns = msg_content_header
    return col_df


def convert_log_columns(df):
    result = df.astype(dtype= {
    "lat":"float64", 
    "lon":"float64", 
    "spd_over_grnd":"float64", 
    "true_course":"float64", 
    "mag_variation":"float64",
    "datestamp":"int64"})
    return result


def convert_weather_columns(df):
    result = df.astype(dtype= {"timestamp_utc" : "datetime64[ns]"})
    return result


def transform_log_data(df):
    msg_content_header = ["status", "lat", "lat_dir", "lon", "lon_dir", "spd_over_grnd", "true_course", "datestamp", "mag_variation", "mag_var_dir"]
    msg_field = "clean_msg"
    
    df[msg_field] = clean_string_field(pd.Series(df["raw_message"]), '[^0-9a-zA-Z,.]+', '')

    df_message = split_string_column(df, msg_field, msg_content_header)
    df_split = df.join(df_message)
    df_split.drop(['raw_message', msg_field], axis=1, inplace=True)
    df_split = convert_log_columns(df_split)

    df_split["datetime"] = df_split.datetime.apply(lambda x: pd.to_datetime(x, unit = 's'))
    df_split["date_hour"] = pd.to_datetime(df_split["datetime"].dt.strftime('%Y-%m-%d %H:00:00'))
    df_split.set_index("datetime", inplace=True)
    return df_split

def transform_weather_data(df):
    df = df.explode("data").reset_index(drop=True)

    weather = df.join(pd.json_normalize(df.data))
    weather.drop(["data"], axis=1, inplace=True)
    weather = convert_weather_columns(weather)
    weather = weather.assign(date_utc = pd.to_datetime(weather["timestamp_utc"].dt.strftime('%Y-%m-%d')))
    weather.set_index("timestamp_utc", inplace=True)
    return weather


def process_log_data(log_data_file):
    log.info("Loading log data from csv.")
    logs = pd.read_csv(log_data_file) 
    log.info("Cleaning and transforming log data.")
    df_log = transform_log_data(logs)
    return df_log


def process_weather_data(weather_data_file):
    log.info("Loading weather data from json.")
    weather = pd.read_json(weather_data_file) 
    log.info("Transforming weather data.")
    df_weather = transform_weather_data(weather)
    return df_weather

