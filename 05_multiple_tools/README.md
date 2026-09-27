# 05 — Multiple Tools

Chapter 04 added the agent loop. The agent can repeatedly move through:

```text
LLM → tool call → tool result → LLM → ... → final answer
```

This chapter keeps that same loop and adds one new concept: **the agent has
several tools, and the LLM chooses which tool to use**.

## Project structure

```text
05_multiple_tools/
├── README.md
├── main.py
└── tools.py
```

## Goal

The agent has three tools:

```text
get_weather()
calculate()
get_city_info()
```

The model now has to select the tool that matches the user's request:

```text
                    ┌── get_weather
                    │
User → LLM → choose ─┼── calculate
                    │
                    └── get_city_info
                           │
                           ▼
                      tool result
                           │
                           ▼
                          LLM
```

The Python program still executes the tool. The model only chooses a tool name
and supplies structured arguments.

## The three tools

### 1. Weather

```python
get_weather(location="Toronto")
```

This tool returns fake weather from a small demo dataset. It does not call a
live weather service because this chapter is about choosing tools, not APIs.

### 2. Calculator

```python
calculate(operation="multiply", a=25, b=8)
```

The calculator supports `add`, `subtract`, `multiply`, and `divide`.

### 3. City information

```python
get_city_info(city="Vancouver")
```

This tool returns a city's country, main language, and approximate population
from another small demo dataset.

## How the model selects a tool

All three tool schemas are sent with every model request:

```python
response = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    tools=TOOLS,
)
```

The descriptions and parameter schemas tell the model what each tool does.
For example:

```text
User: What is 137 multiplied by 42?

Model choice:
    calculate(operation="multiply", a=137, b=42)
```

For a weather question, it should choose `get_weather`. For a question about a
city, it should choose `get_city_info`.

## One request can need several tools

Consider this request:

```text
What is the weather in Toronto, and what is 25 multiplied by 8?
```

The model may request both tools in the same round:

```text
User
 │
 ▼
LLM
 ├── get_weather("Toronto")
 └── calculate("multiply", 25, 8)
          │
          ▼
     tool results
          │
          ▼
         LLM
          │
          ▼
    final answer
```

The code handles this by looping over every requested call:

```python
for tool_call in assistant_message.tool_calls:
    tool_name = tool_call.function.name
    tool_arguments = json.loads(tool_call.function.arguments)
    tool_result = execute_tool(tool_name, tool_arguments)
```

## Multiple tools versus the agent loop

These are separate ideas:

| Chapter | Question it answers |
|---|---|
| 04 — Agent Loop | When should the agent continue acting? |
| 05 — Multiple Tools | Which action should the agent choose? |

The agent loop controls **when to continue**. Multiple tools give the model a
choice about **what to do**.

## Decision versus execution

The model does not run this Python code directly:

```python
calculate("multiply", 25, 8)
```

It returns a structured request similar to:

```text
name: calculate
arguments: {
    "operation": "multiply",
    "a": 25,
    "b": 8
}
```

Python receives that request, executes the function, and returns the result to
the model.

## The manual tool dispatcher

`execute_tool()` connects each tool name to a Python function:

```python
if name == "get_weather":
    return get_weather(...)
elif name == "calculate":
    return calculate(...)
elif name == "get_city_info":
    return get_city_info(...)
```

This repetitive `if/elif` code is intentional. There is no tool registry yet.
With three tools it is manageable, but with 10, 50, or 100 tools it would
become difficult to maintain. That problem gives Chapter 06 a reason to exist.

## Run it

Use the same root `.env` configuration as Chapters 01–04. The selected model
must support OpenAI-compatible tool calling.

From the project root:

```bash
python 05_multiple_tools/main.py
```

On Windows PowerShell:

```powershell
python .\05_multiple_tools\main.py
```

Try each kind of request:

```text
What's the weather in Toronto?

What is 123 multiplied by 456?

Which country is Vancouver in?

What's the weather in Toronto, and what is 45 divided by 5?
```

Watch the `[Tool call]` lines to see which tools the model selects.

## What we have built so far

```text
01  User → LLM → answer
02  Conversation history → LLM → answer
03  LLM → one tool → LLM
04  LLM → tool → LLM → tool → ... → answer
05  LLM → choose between several tools → answer
```

## Current limitations

- Weather and city information come from small demo datasets.
- Tool calls run automatically without user approval.
- Conversation history exists only while the program is running.
- The dispatcher repeats one `if/elif` branch for every tool.
- Each Python function still has a separately written JSON schema.

## Next chapter

The current dispatcher works, but it does not scale:

```python
if name == "tool_1":
    ...
elif name == "tool_2":
    ...
elif name == "tool_3":
    ...
```

Chapter 06 will replace this manual dispatch with a **tool registry**:

```python
tool_registry = {
    "get_weather": get_weather,
    "calculate": calculate,
    "get_city_info": get_city_info,
}
```

That chapter will answer the next question: how do we manage many tools
cleanly?
