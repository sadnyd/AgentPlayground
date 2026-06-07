import requests

from langchain.tools import tool


@tool
def get_weather(city: str) -> str:
    """Get the current weather for a given city."""

    # Step 1: Geocode the city name to latitude/longitude
    geo_resp = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json",
        },
        timeout=10,
    )

    geo_data = geo_resp.json()

    if not geo_data.get("results"):
        return f"Could not find location for '{city}'."

    location = geo_data["results"][0]

    lat = location["latitude"]
    lon = location["longitude"]

    name = location.get("name", city)
    country = location.get("country", "")

    # Step 2: Fetch current weather
    weather_resp = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "wind_speed_10m,"
                "weather_code"
            ),
            "temperature_unit": "celsius",
            "wind_speed_unit": "kmh",
        },
        timeout=10,
    )

    w = weather_resp.json().get("current", {})

    # WMO weather code descriptions
    wmo_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Icy fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Slight showers",
        81: "Moderate showers",
        82: "Violent showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Thunderstorm with heavy hail",
    }

    condition = wmo_codes.get(
        w.get("weather_code"),
        "Unknown",
    )

    return (
        f"Weather in {name}, {country}:\n"
        f"- Condition: {condition}\n"
        f"- Temperature: {w.get('temperature_2m')}°C\n"
        f"- Humidity: {w.get('relative_humidity_2m')}%\n"
        f"- Wind Speed: {w.get('wind_speed_10m')} km/h"
    )