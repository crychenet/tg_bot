from config import OPEN_WEATHER_API_KEY
import aiohttp
import asyncio


async def get_latitude_and_longitude(city_name, api_key):
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f'http://api.openweathermap.org/geo/1.0/direct?q={city_name}&appid={api_key}') as response:
            json_resp = await response.json()
            geographic_coordinates = {'lat': json_resp[0]['lat'], 'lon': json_resp[0]['lon']}
    return geographic_coordinates


async def get_weather_data(geographic_coordinates, api_key):
    async with aiohttp.ClientSession() as session:
        async with session.get(
                f'https://api.openweathermap.org/data/2.5/weather?lat={geographic_coordinates["lat"]}&lon={geographic_coordinates["lon"]}&appid={api_key}&lang=ru&units=metric') as response:
            json_resp = await response.json()
    return json_resp['main']['temp']


async def process_task(city, api_key):
    geographic_coordinates = await get_latitude_and_longitude(city, api_key)
    weather_data = await get_weather_data(geographic_coordinates, api_key)
    result = {city: weather_data}
    print(result)
    return result


asyncio.run(process_task('Сочи', OPEN_WEATHER_API_KEY))
