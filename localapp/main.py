import streamlit as st

import logging
import pydeck
import os

from etl.load import load_data
from etl.transform import process_log_data, process_weather_data

log = logging.getLogger()
ROOT_PATH=os.path.dirname(os.path.abspath(__file__))
DATA_DIR=ROOT_PATH+'/data/'


def calculate_number_of_ships(df_log):
    ''' Logic for kpi 1 '''
    return df_log["device_id"].unique().size


def calculate_hourly_avg_speed(df_log, start_date, end_date):
    ''' Logic for kpi 2 '''
    avg_speed = df_log.sort_index().loc[start_date:end_date].groupby(["device_id", "date_hour"])["spd_over_grnd"].mean().reset_index() 
    avg_speed.columns = [ c.replace("_", " ") for c in avg_speed.columns]
    return avg_speed


def calculate_wind_speed_extremes(df_log, df_weather, ship):
    ''' Logic for kpi 3 '''
    device_days = df_log.loc[df_log["device_id"] == "st-1a2090"]["date_hour"].dt.strftime('%Y-%m-%d').unique()
    weather_data = df_weather.loc[df_weather["date_utc"].isin(device_days)].groupby("date_utc")["wind_spd"].agg(['max', 'min']).reset_index()
    return weather_data.rename(columns={"date_utc": "Date (UTC)", "max": "Max speed in day", "min": "Min speed in day"})


def calculate_weather_on_route(df_log, df_weather, start_date, end_date, ship):
    ''' Logic for kpi 4 '''
    filtered_logs = df_log.loc[df_log["device_id"] == ship].sort_index().loc[start_date:end_date]
    merged_route = filtered_logs.reset_index().merge(df_weather.reset_index(), left_on=["date_hour", "lat", "lon"], right_on=["timestamp_utc", "lat", "lon"])
    result = merged_route[["device_id", "lat", "lon", "temp", "weather.description", "wind_spd" , "timestamp_utc"]].drop_duplicates()
    result = result.assign(date_str=result["timestamp_utc"].dt.strftime('%Y-%m-%d %H:%M'))
    return result


if __name__ == "__main__":
   
    st.title('Shipping Technology™ KPIs')
    
    start_date = '2019-02-13'
    end_date = '2019-02-14'
    ship = 'st-1a2090' 

    df_log = process_log_data(DATA_DIR+'raw_messages.csv')
    df_weather = process_weather_data(DATA_DIR+'weather_data.json')

    # For how many ships do we have available data?
    st.subheader('KPI 1: For how many ships do we have available data?')
    st.metric("Ships", calculate_number_of_ships(df_log), delta=None, delta_color="normal")


    # Avg speed for all available ships for each hour of the date 2019-02-13.
    st.subheader('KPI 2: Hourly average speed on 2019-02-13')
    avg_speed = calculate_hourly_avg_speed(df_log,start_date, end_date)
    st.dataframe(avg_speed)


    # Wind speed extremes for ship ”st-1a2090” .
    st.subheader('KPI 3: Wind speed extremes for ship: st-1a2090')
    weather_data = calculate_wind_speed_extremes(df_log, df_weather,ship)
    st.dataframe(weather_data)


    # Display route data
    st.subheader('KPI 4: Weather data on route for ship: st-1a2090 on day: 2019-02-13')

    dataset = calculate_weather_on_route(df_log, df_weather, start_date, end_date, ship)
    

    layer = pydeck.Layer(
        "TextLayer",
        dataset,
        pickable=True,
        get_position='[lon, lat]',
        get_text="date_str",
        get_size=16,
        get_color=[0, 0, 0],
        get_angle=0,
    )

    view_state = pydeck.ViewState(
        longitude=5.6,
        latitude=51.876222 ,
        zoom=6,
        min_zoom=3,
        max_zoom=15,
        pitch=0,
        bearing=0)

    r = pydeck.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={"text": "Wind speed: {wind_spd}\n Temp: {temp}\n Weather: {weather.description}"},
        map_style=pydeck.map_styles.ROAD,
    )

    st.pydeck_chart(r)
    st.dataframe(dataset)

    try:
        load_data(dataset, "route_weather")
        log.info("route_weather data written to DB.")
    except Exception as e:
        log.error("Could not write to db. Error: " + str(e))
