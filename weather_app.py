# This is a test app created from VSCode agent running Claude Haiku

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import httpx
import os

app = FastAPI()

class WeatherRequest(BaseModel):
    city: str

class ForecastDay(BaseModel):
    date: str
    max_temp: float
    min_temp: float
    weather_code: int
    precipitation_sum: float
    condition: str

class WeatherResponse(BaseModel):
    city: str
    country: str
    latitude: float
    longitude: float
    current_temp: float
    current_condition: str
    current_weather_code: int
    humidity: int
    wind_speed: float
    forecast: List[ForecastDay]

def get_weather_description(code: int) -> str:
    """Map WMO weather code to description."""
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }
    return weather_codes.get(code, "Unknown")

@app.post("/api/weather")
async def get_weather(request: WeatherRequest):
    """
    Get current weather and 5-day forecast for a city.
    Uses Open-Meteo API (free, no API key needed).
    """
    try:
        city = request.city.strip()
        if not city:
            raise HTTPException(status_code=400, detail="City cannot be empty")

        async with httpx.AsyncClient() as client:
            # Step 1: Get coordinates from city name
            geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
            geocoding_response = await client.get(geocoding_url, params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json"
            })
            geocoding_data = geocoding_response.json()

            if not geocoding_data.get("results"):
                raise HTTPException(
                    status_code=404,
                    detail=f"City '{city}' not found"
                )

            result = geocoding_data["results"][0]
            latitude = result["latitude"]
            longitude = result["longitude"]
            city_name = result["name"]
            country = result.get("country", "")

            # Step 2: Get weather data
            weather_url = "https://api.open-meteo.com/v1/forecast"
            weather_response = await client.get(weather_url, params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum",
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "timezone": "auto",
                "forecast_days": 5
            })
            weather_data = weather_response.json()

            # Parse current weather
            current = weather_data["current"]
            current_temp = current["temperature_2m"]
            current_weather_code = current["weather_code"]
            humidity = current["relative_humidity_2m"]
            wind_speed = current["wind_speed_10m"]

            # Parse forecast
            daily = weather_data["daily"]
            forecast = []
            for i in range(len(daily["time"])):
                forecast_day = ForecastDay(
                    date=daily["time"][i],
                    max_temp=daily["temperature_2m_max"][i],
                    min_temp=daily["temperature_2m_min"][i],
                    weather_code=daily["weather_code"][i],
                    precipitation_sum=daily["precipitation_sum"][i],
                    condition=get_weather_description(daily["weather_code"][i])
                )
                forecast.append(forecast_day)

            return WeatherResponse(
                city=city_name,
                country=country,
                latitude=latitude,
                longitude=longitude,
                current_temp=current_temp,
                current_condition=get_weather_description(current_weather_code),
                current_weather_code=current_weather_code,
                humidity=humidity,
                wind_speed=wind_speed,
                forecast=forecast
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Weather service error: {str(e)}"
        )

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
