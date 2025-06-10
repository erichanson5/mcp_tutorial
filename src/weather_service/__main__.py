"""
Weather Service MCP Server Entry Point

Usage:
  python -m src.weather_service

Environment Variables:
  OPENWEATHER_API_KEY - Your OpenWeatherMap API key (get from https://openweathermap.org/api)
"""

from . import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
