def get_weather(location):
    """Return fake weather data for learning tool calling."""
    print(f"\n[Tool] get_weather called for: {location}")

    return {
        "location": location,
        "temperature": "22°C",
        "condition": "sunny",
        "note": "This is demo data, not live weather.",
    }


# This JSON schema tells the model how to call get_weather.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get demo weather information for a location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and country, for example Toronto, Canada",
                    }
                },
                "required": ["location"],
            },
        },
    }
]


# This dictionary connects a tool name to the real Python function.
AVAILABLE_TOOLS = {
    "get_weather": get_weather,
}
