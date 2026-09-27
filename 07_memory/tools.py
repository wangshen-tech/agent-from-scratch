import json

from registry import ToolRegistry


# Create one registry shared by the agent and all tools.
registry = ToolRegistry()


# =========================================================
# Tool 1: Weather
# =========================================================

def get_weather(location: str) -> str:
    """Return fake weather data for learning how tool selection works."""
    weather_data = {
        "toronto": {
            "temperature": 20,
            "condition": "Sunny",
        },
        "vancouver": {
            "temperature": 16,
            "condition": "Rainy",
        },
        "new york": {
            "temperature": 23,
            "condition": "Cloudy",
        },
    }

    weather = weather_data.get(
        location.lower(),
        {
            "temperature": "unknown",
            "condition": "unknown",
        },
    )

    return json.dumps(
        {
            "location": location,
            "temperature": weather["temperature"],
            "condition": weather["condition"],
            "note": "This is demo data, not live weather.",
        }
    )


GET_WEATHER_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get demo weather information for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city to get weather for.",
                }
            },
            "required": ["location"],
            "additionalProperties": False,
        },
    },
}


registry.register(
    name="get_weather",
    function=get_weather,
    schema=GET_WEATHER_SCHEMA,
)


# =========================================================
# Tool 2: Calculator
# =========================================================

def calculate(operation: str, a: float, b: float) -> str:
    """Perform one basic arithmetic operation."""
    if operation == "add":
        result = a + b
    elif operation == "subtract":
        result = a - b
    elif operation == "multiply":
        result = a * b
    elif operation == "divide":
        if b == 0:
            return json.dumps({"error": "Cannot divide by zero."})
        result = a / b
    else:
        return json.dumps({"error": f"Unknown operation: {operation}"})

    return json.dumps(
        {
            "operation": operation,
            "a": a,
            "b": b,
            "result": result,
        }
    )


CALCULATE_SCHEMA = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "Perform a basic mathematical calculation.",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                    "description": "The mathematical operation.",
                },
                "a": {
                    "type": "number",
                    "description": "The first number.",
                },
                "b": {
                    "type": "number",
                    "description": "The second number.",
                },
            },
            "required": ["operation", "a", "b"],
            "additionalProperties": False,
        },
    },
}


registry.register(
    name="calculate",
    function=calculate,
    schema=CALCULATE_SCHEMA,
)


# =========================================================
# Tool 3: City Information
# =========================================================

def get_city_info(city: str) -> str:
    """Return basic information from a small demo city database."""
    city_data = {
        "toronto": {
            "country": "Canada",
            "language": "English",
            "population": "about 3 million",
        },
        "vancouver": {
            "country": "Canada",
            "language": "English",
            "population": "about 700 thousand",
        },
        "new york": {
            "country": "United States",
            "language": "English",
            "population": "about 8 million",
        },
    }

    info = city_data.get(city.lower())

    if info is None:
        return json.dumps(
            {
                "city": city,
                "error": "City not found in demo database.",
            }
        )

    return json.dumps(
        {
            "city": city,
            **info,
        }
    )


GET_CITY_INFO_SCHEMA = {
    "type": "function",
    "function": {
        "name": "get_city_info",
        "description": "Get basic information about a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city to get information about.",
                }
            },
            "required": ["city"],
            "additionalProperties": False,
        },
    },
}


registry.register(
    name="get_city_info",
    function=get_city_info,
    schema=GET_CITY_INFO_SCHEMA,
)
