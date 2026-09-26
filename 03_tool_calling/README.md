# 03 — Tool Calling

Chapter 02 gave the model conversation memory. Chapter 03 adds one new ability: the model can ask your Python program to run a function.

```text
User → model → tool call → Python function
                ↑              │
                └─ tool result ┘
                       │
                       ▼
                  final answer
```

## Project structure

```text
03_tool_calling/
├── README.md
├── agent.py
└── tools.py
```

- `tools.py` contains the real Python function and its JSON schema.
- `agent.py` talks to the model, executes requested tools, and returns their results.

## The weather tool

`get_weather()` is deliberately simple:

```python
def get_weather(location):
    return {
        "location": location,
        "temperature": "22°C",
        "condition": "sunny",
        "note": "This is demo data, not live weather.",
    }
```

It returns fake data so this chapter can focus only on tool calling. No weather API or additional API key is needed.

## The tool definition

The model cannot read the Python function directly. We describe the function with a JSON schema:

```python
{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get demo weather information for a location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            },
            "required": ["location"],
        },
    },
}
```

This tells the model:

- which tool exists
- what the tool does
- which arguments it needs

The model requests a tool call, but Python executes the actual function.

## The five-step flow

1. Send the user's message and the tool definition to the model.
2. Receive a tool call such as `get_weather(location="Toronto")`.
3. Execute `get_weather()` in Python.
4. Add the tool result to `messages`.
5. Call the model again to produce the final answer.

## Run it

Use the same root `.env` file as the earlier chapters. The selected model must support OpenAI-compatible tool calling.

```bash
cd ~/Desktop/agent-from-scratch
source .venv/bin/activate
python 03_tool_calling/agent.py
```

Try a tool question:

```text
You: What is the weather in Toronto?

[Tool] get_weather called for: Toronto
Assistant: The demo weather for Toronto is sunny and 22°C.
```

Then try a normal question:

```text
You: What is 2 + 2?
Assistant: 4
```

The model should call `get_weather` only when it needs weather information.

## Current limitations

- The weather is fake demonstration data.
- There is only one tool.
- The program handles one round of tool calls before producing an answer.
- Tool permissions and safety checks are not implemented yet.
