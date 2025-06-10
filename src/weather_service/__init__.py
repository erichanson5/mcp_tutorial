"""
Weather Service MCP Server

This server demonstrates API integration and external data fetching with:
- Weather data from OpenWeatherMap API
- Location-based queries
- Caching for performance
- Error handling for API failures
- Multiple weather data formats

Features:
- Current weather by city or coordinates
- Weather forecasts
- Historical weather data
- Weather alerts and warnings
- Multiple units (metric, imperial)
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import aiohttp
import asyncio
from pathlib import Path

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    GetResourceResult,
    ListResourcesResult,
    ListToolsResult,
    Resource,
    TextContent,
    Tool,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Weather API configuration
# Note: In a real application, use environment variables or config files
DEFAULT_API_KEY = "demo_key"  # Replace with actual API key
BASE_URL = "http://api.openweathermap.org/data/2.5"

# Simple in-memory cache
weather_cache = {}
CACHE_DURATION = timedelta(minutes=10)

# MCP Server
server = Server("weather-service-mcp-server")


class WeatherService:
    """Weather service with API integration and caching"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY", DEFAULT_API_KEY)
        self.session = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def _cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate cache key"""
        sorted_params = sorted(params.items())
        return f"{endpoint}:{hash(str(sorted_params))}"
    
    def _is_cache_valid(self, timestamp: datetime) -> bool:
        """Check if cached data is still valid"""
        return datetime.now() - timestamp < CACHE_DURATION
    
    async def _make_api_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make API request with caching"""
        # Check cache first
        cache_key = self._cache_key(endpoint, params)
        if cache_key in weather_cache:
            cached_data, timestamp = weather_cache[cache_key]
            if self._is_cache_valid(timestamp):
                logger.info(f"Cache hit for {endpoint}")
                return cached_data
        
        # Make API request
        params["appid"] = self.api_key
        url = f"{BASE_URL}/{endpoint}"
        
        try:
            session = await self.get_session()
            async with session.get(url, params=params) as response:
                if response.status == 401:
                    return {"error": "Invalid API key. Please set OPENWEATHER_API_KEY environment variable."}
                elif response.status == 404:
                    return {"error": "Location not found"}
                elif response.status != 200:
                    return {"error": f"API error: {response.status}"}
                
                data = await response.json()
                
                # Cache the result
                weather_cache[cache_key] = (data, datetime.now())
                logger.info(f"Cached new data for {endpoint}")
                
                return data
                
        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error: {e}")
            return {"error": f"Network error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"error": f"Unexpected error: {str(e)}"}
    
    async def get_current_weather(self, location: str, units: str = "metric") -> Dict[str, Any]:
        """Get current weather for a location"""
        params = {"q": location, "units": units}
        return await self._make_api_request("weather", params)
    
    async def get_current_weather_by_coords(self, lat: float, lon: float, units: str = "metric") -> Dict[str, Any]:
        """Get current weather by coordinates"""
        params = {"lat": lat, "lon": lon, "units": units}
        return await self._make_api_request("weather", params)
    
    async def get_forecast(self, location: str, units: str = "metric") -> Dict[str, Any]:
        """Get 5-day weather forecast"""
        params = {"q": location, "units": units}
        return await self._make_api_request("forecast", params)
    
    async def get_forecast_by_coords(self, lat: float, lon: float, units: str = "metric") -> Dict[str, Any]:
        """Get 5-day weather forecast by coordinates"""
        params = {"lat": lat, "lon": lon, "units": units}
        return await self._make_api_request("forecast", params)


# Initialize weather service
weather_service = WeatherService()


@server.list_tools()
async def handle_list_tools() -> ListToolsResult:
    """List available weather tools"""
    tools = [
        Tool(
            name="get_current_weather",
            description="Get current weather conditions for a specific location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, state/country (e.g., 'London,UK' or 'New York,NY,US')"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial", "kelvin"],
                        "description": "Temperature units (metric=Celsius, imperial=Fahrenheit, kelvin=Kelvin)",
                        "default": "metric"
                    }
                },
                "required": ["location"]
            }
        ),
        Tool(
            name="get_weather_by_coordinates",
            description="Get current weather by latitude and longitude",
            inputSchema={
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Latitude coordinate",
                        "minimum": -90,
                        "maximum": 90
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude coordinate",
                        "minimum": -180,
                        "maximum": 180
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial", "kelvin"],
                        "description": "Temperature units",
                        "default": "metric"
                    }
                },
                "required": ["latitude", "longitude"]
            }
        ),
        Tool(
            name="get_weather_forecast",
            description="Get 5-day weather forecast for a location",
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, state/country"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial", "kelvin"],
                        "description": "Temperature units",
                        "default": "metric"
                    }
                },
                "required": ["location"]
            }
        ),
        Tool(
            name="get_forecast_by_coordinates",
            description="Get 5-day weather forecast by coordinates",
            inputSchema={
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Latitude coordinate",
                        "minimum": -90,
                        "maximum": 90
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude coordinate",
                        "minimum": -180,
                        "maximum": 180
                    },
                    "units": {
                        "type": "string",
                        "enum": ["metric", "imperial", "kelvin"],
                        "description": "Temperature units",
                        "default": "metric"
                    }
                },
                "required": ["latitude", "longitude"]
            }
        ),
        Tool(
            name="parse_weather_data",
            description="Parse and format weather data into human-readable format",
            inputSchema={
                "type": "object",
                "properties": {
                    "weather_data": {
                        "type": "object",
                        "description": "Raw weather data from API"
                    }
                },
                "required": ["weather_data"]
            }
        )
    ]
    
    return ListToolsResult(tools=tools)


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool execution"""
    try:
        if name == "get_current_weather":
            return await handle_current_weather(arguments)
        elif name == "get_weather_by_coordinates":
            return await handle_weather_by_coordinates(arguments)
        elif name == "get_weather_forecast":
            return await handle_weather_forecast(arguments)
        elif name == "get_forecast_by_coordinates":
            return await handle_forecast_by_coordinates(arguments)
        elif name == "parse_weather_data":
            return await handle_parse_weather_data(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")],
            isError=True
        )


async def handle_current_weather(arguments: Dict[str, Any]) -> CallToolResult:
    """Get current weather for a location"""
    location = arguments["location"]
    units = arguments.get("units", "metric")
    
    weather_data = await weather_service.get_current_weather(location, units)
    
    if "error" in weather_data:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Weather API Error: {weather_data['error']}")],
            isError=True
        )
    
    # Format the weather data
    formatted_weather = format_current_weather(weather_data, units)
    
    return CallToolResult(
        content=[TextContent(type="text", text=formatted_weather)]
    )


async def handle_weather_by_coordinates(arguments: Dict[str, Any]) -> CallToolResult:
    """Get current weather by coordinates"""
    lat = arguments["latitude"]
    lon = arguments["longitude"]
    units = arguments.get("units", "metric")
    
    weather_data = await weather_service.get_current_weather_by_coords(lat, lon, units)
    
    if "error" in weather_data:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Weather API Error: {weather_data['error']}")],
            isError=True
        )
    
    formatted_weather = format_current_weather(weather_data, units)
    
    return CallToolResult(
        content=[TextContent(type="text", text=formatted_weather)]
    )


async def handle_weather_forecast(arguments: Dict[str, Any]) -> CallToolResult:
    """Get weather forecast for a location"""
    location = arguments["location"]
    units = arguments.get("units", "metric")
    
    forecast_data = await weather_service.get_forecast(location, units)
    
    if "error" in forecast_data:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Weather API Error: {forecast_data['error']}")],
            isError=True
        )
    
    formatted_forecast = format_forecast(forecast_data, units)
    
    return CallToolResult(
        content=[TextContent(type="text", text=formatted_forecast)]
    )


async def handle_forecast_by_coordinates(arguments: Dict[str, Any]) -> CallToolResult:
    """Get weather forecast by coordinates"""
    lat = arguments["latitude"]
    lon = arguments["longitude"]
    units = arguments.get("units", "metric")
    
    forecast_data = await weather_service.get_forecast_by_coords(lat, lon, units)
    
    if "error" in forecast_data:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Weather API Error: {forecast_data['error']}")],
            isError=True
        )
    
    formatted_forecast = format_forecast(forecast_data, units)
    
    return CallToolResult(
        content=[TextContent(type="text", text=formatted_forecast)]
    )


async def handle_parse_weather_data(arguments: Dict[str, Any]) -> CallToolResult:
    """Parse and format raw weather data"""
    weather_data = arguments["weather_data"]
    
    if "main" in weather_data:
        # Current weather data
        formatted = format_current_weather(weather_data, "metric")
    elif "list" in weather_data:
        # Forecast data
        formatted = format_forecast(weather_data, "metric")
    else:
        formatted = f"Raw weather data:\n{json.dumps(weather_data, indent=2)}"
    
    return CallToolResult(
        content=[TextContent(type="text", text=formatted)]
    )


def format_current_weather(data: Dict[str, Any], units: str) -> str:
    """Format current weather data into readable text"""
    if "main" not in data or "weather" not in data:
        return f"Invalid weather data:\n{json.dumps(data, indent=2)}"
    
    # Unit symbols
    temp_unit = "°C" if units == "metric" else "°F" if units == "imperial" else "K"
    speed_unit = "m/s" if units == "metric" else "mph" if units == "imperial" else "m/s"
    
    location = data.get("name", "Unknown")
    country = data.get("sys", {}).get("country", "")
    if country:
        location += f", {country}"
    
    weather = data["weather"][0]
    main = data["main"]
    wind = data.get("wind", {})
    clouds = data.get("clouds", {})
    
    formatted = f"""🌤️ Current Weather for {location}

🌡️ Temperature: {main['temp']}{temp_unit} (feels like {main['feels_like']}{temp_unit})
📊 Conditions: {weather['main']} - {weather['description'].title()}
💧 Humidity: {main['humidity']}%
🌬️ Wind: {wind.get('speed', 0)} {speed_unit}"""
    
    if wind.get('deg'):
        formatted += f" from {wind['deg']}°"
    
    formatted += f"""
☁️ Cloudiness: {clouds.get('all', 0)}%
🔽 Pressure: {main['pressure']} hPa"""
    
    if 'visibility' in data:
        formatted += f"\n👁️ Visibility: {data['visibility']/1000:.1f} km"
    
    # Add sunrise/sunset if available
    if 'sys' in data and 'sunrise' in data['sys']:
        sunrise = datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')
        sunset = datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')
        formatted += f"\n🌅 Sunrise: {sunrise} | 🌇 Sunset: {sunset}"
    
    formatted += f"\n\n📅 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return formatted


def format_forecast(data: Dict[str, Any], units: str) -> str:
    """Format forecast data into readable text"""
    if "list" not in data or "city" not in data:
        return f"Invalid forecast data:\n{json.dumps(data, indent=2)}"
    
    temp_unit = "°C" if units == "metric" else "°F" if units == "imperial" else "K"
    
    city = data["city"]["name"]
    country = data["city"].get("country", "")
    if country:
        city += f", {country}"
    
    formatted = f"📅 5-Day Weather Forecast for {city}\n{'='*50}\n"
    
    # Group forecasts by day
    daily_forecasts = {}
    for item in data["list"]:
        date_time = datetime.fromtimestamp(item["dt"])
        date_key = date_time.strftime('%Y-%m-%d')
        
        if date_key not in daily_forecasts:
            daily_forecasts[date_key] = []
        daily_forecasts[date_key].append(item)
    
    # Format each day
    for date_key in sorted(daily_forecasts.keys())[:5]:  # Only show 5 days
        day_data = daily_forecasts[date_key]
        date_obj = datetime.strptime(date_key, '%Y-%m-%d')
        day_name = date_obj.strftime('%A, %B %d')
        
        formatted += f"\n📆 {day_name}\n"
        formatted += "-" * 30 + "\n"
        
        # Find min/max temps for the day
        temps = [item["main"]["temp"] for item in day_data]
        min_temp = min(temps)
        max_temp = max(temps)
        
        # Get most common weather condition
        conditions = [item["weather"][0]["description"] for item in day_data]
        main_condition = max(set(conditions), key=conditions.count)
        
        formatted += f"🌡️ Temperature: {min_temp:.1f}{temp_unit} - {max_temp:.1f}{temp_unit}\n"
        formatted += f"🌤️ Conditions: {main_condition.title()}\n"
        
        # Show detailed forecast for key times
        key_times = []
        for item in day_data:
            hour = datetime.fromtimestamp(item["dt"]).hour
            if hour in [6, 12, 18]:  # Morning, noon, evening
                key_times.append(item)
        
        if key_times:
            formatted += "⏰ Hourly Details:\n"
            for item in key_times:
                time_str = datetime.fromtimestamp(item["dt"]).strftime('%H:%M')
                temp = item["main"]["temp"]
                desc = item["weather"][0]["description"]
                formatted += f"  {time_str}: {temp}{temp_unit}, {desc}\n"
        
        formatted += "\n"
    
    formatted += f"📊 Data provided by OpenWeatherMap\n"
    formatted += f"🕐 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return formatted


@server.list_resources()
async def handle_list_resources() -> ListResourcesResult:
    """List available weather resources"""
    resources = [
        Resource(
            uri="weather://cache",
            name="Weather Cache Status",
            description="Information about cached weather data",
            mimeType="application/json"
        ),
        Resource(
            uri="weather://api-info",
            name="Weather API Information",
            description="Information about the weather API service",
            mimeType="text/plain"
        )
    ]
    
    return ListResourcesResult(resources=resources)


@server.get_resource()
async def handle_get_resource(uri: str) -> GetResourceResult:
    """Handle resource requests"""
    try:
        if uri == "weather://cache":
            cache_info = {
                "cache_entries": len(weather_cache),
                "cache_duration_minutes": CACHE_DURATION.total_seconds() / 60,
                "cached_items": []
            }
            
            for key, (data, timestamp) in weather_cache.items():
                cache_info["cached_items"].append({
                    "key": key,
                    "timestamp": timestamp.isoformat(),
                    "age_minutes": (datetime.now() - timestamp).total_seconds() / 60,
                    "valid": weather_service._is_cache_valid(timestamp)
                })
            
            return GetResourceResult(
                contents=[
                    TextContent(type="text", text=json.dumps(cache_info, indent=2))
                ]
            )
            
        elif uri == "weather://api-info":
            api_info = f"""Weather Service API Information
=====================================

Service Provider: OpenWeatherMap
Base URL: {BASE_URL}
API Key Status: {'Configured' if weather_service.api_key != DEFAULT_API_KEY else 'Using Demo Key'}

Available Endpoints:
- Current Weather: /weather
- 5-Day Forecast: /forecast

Supported Features:
✅ Current weather conditions
✅ 5-day / 3-hour forecasts  
✅ Multiple units (metric, imperial, kelvin)
✅ Location by city name or coordinates
✅ Caching for performance
✅ Error handling and validation

Cache Configuration:
- Duration: {CACHE_DURATION.total_seconds() / 60} minutes
- Current entries: {len(weather_cache)}

Note: To use real weather data, set the OPENWEATHER_API_KEY environment variable.
Get your free API key at: https://openweathermap.org/api
"""
            
            return GetResourceResult(
                contents=[
                    TextContent(type="text", text=api_info)
                ]
            )
            
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
            
    except Exception as e:
        logger.error(f"Error getting resource {uri}: {e}")
        raise


async def main():
    """Main server function"""
    logger.info("Starting Weather Service MCP Server")
    
    try:
        async with stdio_server() as streams:
            await server.run(
                streams[0], streams[1],
                InitializationOptions(
                    server_name="weather-service-mcp-server",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
    finally:
        # Clean up HTTP session
        await weather_service.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
