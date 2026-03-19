import asyncio
import pandas as pd
import datetime
from haversine import haversine, Unit
from google.maps import places_v1
from google.type import latlng_pb2
import random
import os


async def nearby_search():
    center_lat = 25.023032939526363
    center_lng = 121.55546541139819
    center_coord = (center_lat, center_lng)
    step_lat = 0.0018
    step_lng = 0.0020
    radius_meters = 150.0       
    client = places_v1.PlacesAsyncClient(
        client_options={"api_key": "AIzaSyBhKSxCIbPgevpHRUy29u_MySXk_5Q6grY"}
    )
    languageCode = "zh-TW"
    search_query = "晚餐"
    min_place_rating = 3.0
    fieldMask = "places.displayName,places.id,places.currentOpeningHours"
    priceLevels = [
        places_v1.types.PriceLevel.PRICE_LEVEL_INEXPENSIVE,
        places_v1.types.PriceLevel.PRICE_LEVEL_MODERATE,
        places_v1.types.PriceLevel.PRICE_LEVEL_EXPENSIVE,
        places_v1.types.PriceLevel.PRICE_LEVEL_VERY_EXPENSIVE
    ]
    result = {}
    data = []
    for i in range(-2, 3):
        for j in range(-2, 3):
            grid_lat = center_lat + (i * step_lat)
            grid_lng = center_lng + (j * step_lng)
            grid_coord = (grid_lat, grid_lng)
            distance_to_center = haversine(center_coord, grid_coord, unit=Unit.METERS)
            if distance_to_center > 300.0:
                continue
            center_point = latlng_pb2.LatLng(latitude=grid_lat, longitude=grid_lng)
            circle_area = places_v1.types.Circle(
                center=center_point,
                radius=radius_meters
            )
            location_bias = places_v1.SearchTextRequest.LocationBias(
                circle=circle_area
            )
            request = places_v1.SearchTextRequest(
                text_query=search_query,
                location_bias=location_bias,
                min_rating=min_place_rating,
                open_now=False,
                language_code=languageCode,
                price_levels=priceLevels
            )
            response = await client.search_text(request=request, metadata=[("x-goog-fieldmask",fieldMask)]) 
            places = response.places

            for place in places:
                if place.id not in result:
                    periods = place.current_opening_hours.periods
                    processed_time = time_process(periods)
                    #TODO: Add name and time into list: data
                    curr = [place.display_name.text, processed_time]
                    data.append(curr)
                    result[place.id] = place.display_name.text
            #TODO: Initialize DataFrame and output data as csv
        
    column = ["name", "time"]
    index = list(range(len(result)))
    df = pd.DataFrame(data = data, index = index, columns = column) 
    df.to_csv("result.csv")
    return 

def time_process(periods):
    result = {}
    for period in periods:
        year = period.open.date.year
        month = period.open.date.month
        day = period.open.date.day
        date = datetime.datetime(year, month, day)
        if date not in result:
            result[date] = []
        open_minute = period.open.minute
        open_hour = period.open.hour
        open_date = datetime.datetime(year, month, day, open_hour, open_minute)
        close_month = period.close.date.month
        close_day = period.close.date.day
        close_minute = period.close.minute
        close_hour = period.close.hour
        close_date = datetime.datetime(year, close_month, close_day, close_hour, close_minute)
        result[date].append((open_date, close_date))        
    return result
    
def isOpen(result: dict) -> bool:
    t_year = datetime.datetime.today().year
    t_month = datetime.datetime.today().month
    t_day = datetime.datetime.today().day
    today = datetime.datetime.today()
    verified_today = datetime.datetime(t_year, t_month, t_day)
    if verified_today not in result:
        return False
    for interval in result[verified_today]:
        start = interval[0]
        end = interval[1]
        if today >= start and today <= end:
            return True
    return False

def get_opened():
    df = pd.read_csv("result.csv")    
    time = df["time"]
    name = df["name"]
    result = []
    for i in range(len(time)):
        if isOpen(eval(time[i])):
            result.append(name[i])
    return result

if __name__ == "__main__":
    #TODO: once per 7 days
    m_timestamp = os.path.getmtime("result.csv")
    today_timestamp = datetime.datetime.today().timestamp()
    if today_timestamp >= m_timestamp + 604800:
        asyncio.run(nearby_search())
    result = get_opened()
    
    #TODO: randomizera
    idx = random.randint(0, len(result) - 1)
    print(result[idx])

