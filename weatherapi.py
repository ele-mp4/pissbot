import requests
import datetime
import pytz
from timezonefinder import TimezoneFinder

def error_message(status_code):
    print(f"Failed to send request, error code: {str(status_code)}")

class WeatherInfo():
    temperature = None
    feelslike = None
    humidity = None
    pressure = None
    clouds = None
    windspeed = None

class PollutionInfo():
    aqi = None
    airquality = None

class City():
    def __init__(self, city_name, key):
        # uses the geo API cuz the other way to do it will be deprecated soon!
        r = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=3&appid={key}") # city name, state code, country code
        if r.status_code != 200:
            error_message(r.status_code)
            return
        obj = TimezoneFinder()
  
        info = r.json()
        self.name = info[0]["name"]
        self.latitude = info[0]["lat"]
        self.longitude = info[0]["lon"]
        self.country = info[0]["country"]
        timezone = obj.timezone_at(lng=self.longitude, lat=self.latitude)
        self.time = datetime.datetime.now(pytz.timezone(timezone)).strftime("%#I:%M %p")
        if "state" in info[0]:
            self.state = info[0]["state"]
        else:
            self.state = None
    def Weather(self, unit, key):
        if unit.lower() == "kelvin" or unit.lower() == "k":
            unit = "standard"
        elif unit.lower() == "celsius" or unit.lower() == "c":
            unit = "metric"
        elif unit.lower() == "fahrenheit" or unit.lower() == "f":
            unit = "imperial"
        else:
            unit = "metric"
        r = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={self.latitude}&lon={self.longitude}&appid={key}&units={unit}")
        if r.status_code != 200:
            error_message(r.status_code)
            return
        info = r.json()
        wi = WeatherInfo()
        wi.temperature = round(info["main"]["temp"])
        wi.feelslike = round(info["main"]["feels_like"])
        wi.humidity = str(info["main"]["humidity"])+"%"
        wi.pressure = str(info["main"]["pressure"])+"hPa"
        wi.clouds = info["weather"][0]["main"]
        if unit == "metric" or unit == "standard":
            wi.windspeed = str(round(info["wind"]["speed"] * 3.6))+"kmh"
        else:
            wi.windspeed = str(round(info["wind"]["speed"]))+"mph"
        return wi
    def Pollution(self, key):
        r = requests.get(f"http://api.airvisual.com/v2/nearest_city?lat={self.latitude}&lon={self.longitude}&key={key}")
        info = r.json()
        if info["status"] != "success":
            error_message(str(r.status_code) + " " + info["status"])
            return
        pi = PollutionInfo()
        pi.aqi = info["data"]["current"]["pollution"]["aqius"]
        pi.airquality = "healthy"
        if pi.aqi >= 50:
            pi.airquality = "average"
        if pi.aqi >= 100:
            pi.airquality = "poor"
        if pi.aqi >= 150:
            pi.airquality = "unhealthy"
        if pi.aqi >= 200:
            pi.airquality = "hazardous"
        return pi