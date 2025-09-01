import os
import requests
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.tools import ToolContext
from google.genai import types as genai_types

# --- Load environment variables ---
load_dotenv()

# --- Tool Definition ---
def get_weather_data(location: str, tool_context: ToolContext) -> str:
    """
    Fetches current weather data from the Weatherbit API for a specified city.
    You must have your WEATHERBIT_API_KEY in a .env file.
    """
    print(f"--- Tool triggered: get_weather_data for '{location}' ---")
    api_key = os.getenv("WEATHERBIT_API_KEY")
    if not api_key:
        return "Error: WEATHERBIT_API_KEY not found in environment variables. Please add it to your .env file."

    base_url = "https://api.weatherbit.io/v2.0/current"
    params = {
        "city": location,
        "key": api_key,
        "units": "I"  # Request units in Fahrenheit, mph
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        weather = response.json()['data'][0]

        # Formatting a user-friendly response string
        report = (
            f"Weather in {weather['city_name']}, {weather['country_code']}:\n"
            f"- Temperature: {weather['temp']}°F (Feels like: {weather['app_temp']}°F)\n"
            f"- Conditions: {weather['weather']['description']}\n"
            f"- Wind: {weather['wind_spd']:.1f} mph from the {weather['wind_cdir']}\n"
            f"- Humidity: {weather['rh']}%\n"
            f"- UV Index: {weather['uv']:.1f}"
        )
        return report

    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err} - Check your city name and API key."
    except Exception as e:
        return f"An error occurred: {e}"

# --- Agent Definition ---
root_agent = Agent(
    model="gemini-2.5-flash",
    name="Weather_Agent",
    instruction='''
    You are a friendly and precise weather assistant. Your primary purpose is to provide current weather information for any location using the Weatherbit API.

    **Your Workflow:**

    1.  **Be Conversational:** Always be polite. If a user greets you, greet them back before doing anything else and ask them what location's weather would they like to know.
    2.  **Use Your Tool:** When a user asks for the weather, you MUST use the `get_weather_data` tool to fetch the information. Pass the location they ask for directly to the tool.
    3.  **Present the Data:** When you get the data back from the tool, present it to the user in a clear, easy-to-read format.
    4.  **Handle Errors:** If the tool returns an error (e.g., city not found, API key issue), politely inform the user about the error and suggest a solution, like checking the spelling of the city.
    5.  **Handle Off-Topic Questions:** If the user asks about something other than the weather, use your general knowledge to provide a helpful response, and then gently ask if they would like a weather update for a specific location.
    ''',
    tools=[get_weather_data],
    generate_content_config=genai_types.GenerateContentConfig(temperature=0.7),
)
