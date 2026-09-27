def get_weather(location):
    """Return fake weather data for learning how an agent loop works."""
    return {
        "location": location,
        "temperature_c": 22,
        "condition": "sunny",
        "note": "This is demo data, not live weather.",
    }


def celsius_to_fahrenheit(celsius):
    """Convert a Celsius temperature to Fahrenheit."""
    fahrenheit = celsius * 9 / 5 + 32
    return {
        "celsius": celsius,
        "fahrenheit": round(fahrenheit, 1),
    }


# These schemas tell the model which tools exist and how to call them.
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
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "celsius_to_fahrenheit",
            "description": "Convert a temperature from Celsius to Fahrenheit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "celsius": {
                        "type": "number",
                        "description": "The temperature in degrees Celsius",
                    }
                },
                "required": ["celsius"],
                "additionalProperties": False,
            },
        },
    },
]


# This dictionary connects tool names to the real Python functions.
AVAILABLE_TOOLS = {
    "get_weather": get_weather,
    "celsius_to_fahrenheit": celsius_to_fahrenheit,
}
