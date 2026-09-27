# 06 — Tool Registry

Chapter 05 gave the agent three tools and let the model choose between them.
However, Python still found each tool with a manual dispatcher:

```python
if name == "get_weather":
    ...
elif name == "calculate":
    ...
elif name == "get_city_info":
    ...
```

This works with three tools, but the chain grows every time we add another
tool. Chapter 06 introduces one new concept: a **tool registry**.

The visible behavior stays the same. Only the internal tool lookup changes:

```text
Chapter 05                      Chapter 06

tool name                       tool name
    ↓                               ↓
if / elif / elif                Tool Registry
    ↓                               ↓
Python function                 Python function
```

## Project structure

```text
06_tool_registry/
├── README.md
├── main.py
├── registry.py
└── tools.py
```

- `main.py` contains the conversation and agent loop.
- `tools.py` contains the same functions and schemas as Chapter 05, plus their
  registration.
- `registry.py` stores, finds, and executes tools.

## What is a registry?

A registry is a place that stores objects by name. The basic idea is an
ordinary Python dictionary:

```python
functions = {
    "get_weather": get_weather,
    "calculate": calculate,
    "get_city_info": get_city_info,
}
```

The values above are function objects. Writing `get_weather` without
parentheses refers to the function itself; it does not call the function yet.

If a model requests `calculate`, Python can retrieve it directly:

```python
function = functions["calculate"]
```

This is approximately the same as:

```python
function = calculate
```

## The `ToolRegistry` class

Our registry stores two collections:

```python
self.functions = {}
self.schemas = []
```

They serve different consumers:

| Stored value | Used by |
|---|---|
| Python functions | The runtime that executes tool calls |
| JSON schemas | The model that decides which tool to request |

The schemas are still written manually in this chapter. Automatic schema
generation and decorators are deliberately left for later chapters.

## Registering a tool

Each tool is registered after its function and schema are defined:

```python
registry.register(
    name="get_weather",
    function=get_weather,
    schema=GET_WEATHER_SCHEMA,
)
```

The registry stores the function by name and appends the schema:

```python
self.functions[name] = function
self.schemas.append(schema)
```

After all three registrations, the function dictionary looks approximately
like this:

```python
{
    "get_weather": get_weather,
    "calculate": calculate,
    "get_city_info": get_city_info,
}
```

The registry rejects duplicate names so one tool cannot silently replace
another tool.

## Sending schemas to the model

Chapter 05 sent a module-level `TOOLS` list:

```python
tools=TOOLS
```

Chapter 06 asks the registry for those same schemas:

```python
tools=registry.get_schemas()
```

The model therefore sees the same three tool descriptions as before.

## Finding and executing a tool

The key change is inside `ToolRegistry.execute()`:

```python
function = self.functions[name]
return function(**arguments)
```

Suppose the model returns:

```python
name = "get_weather"
arguments = {
    "location": "Toronto",
}
```

The first line retrieves the registered function:

```python
function = self.functions["get_weather"]
```

The second line executes it:

```python
function(**arguments)
```

`**arguments` unpacks dictionary entries into named arguments, so the call is
equivalent to:

```python
get_weather(location="Toronto")
```

The same generic code also handles the calculator. Given:

```python
arguments = {
    "operation": "multiply",
    "a": 10,
    "b": 20,
}
```

the call becomes:

```python
calculate(
    operation="multiply",
    a=10,
    b=20,
)
```

## Before and after

Chapter 05 required a branch for every tool:

```python
if name == "get_weather":
    return get_weather(location=arguments["location"])
elif name == "calculate":
    return calculate(
        operation=arguments["operation"],
        a=arguments["a"],
        b=arguments["b"],
    )
elif name == "get_city_info":
    return get_city_info(city=arguments["city"])
```

Chapter 06 replaces the complete chain with:

```python
function = self.functions[name]
return function(**arguments)
```

Adding a fourth or hundredth tool no longer requires changing the execution
logic.

## Separation of responsibilities

The files now have clearer jobs:

```text
main.py
├── conversation history
├── model calls
└── agent loop

tools.py
├── tool functions
├── manually written schemas
└── registrations

registry.py
├── stores functions and schemas
├── finds functions by name
└── executes functions
```

The agent loop no longer needs to know which tools exist. It only calls:

```python
registry.execute(
    name=tool_name,
    arguments=tool_arguments,
)
```

## Run it

Use the same root `.env` configuration as the earlier chapters. The selected
model must support OpenAI-compatible tool calling.

From the project root:

```bash
python 06_tool_registry/main.py
```

On Windows PowerShell:

```powershell
python .\06_tool_registry\main.py
```

Try the same requests as Chapter 05:

```text
What's the weather in Toronto?

Calculate 123 * 456.

Which country is Vancouver in?

What's the weather in Toronto, and what is 45 divided by 5?
```

The results should be the same. This is a refactoring chapter: the program’s
organization, scalability, and maintainability improve without adding a new
user-facing capability.

## Current limitation

The registry removes manual dispatch, but defining one tool still requires
repetition:

```text
Python function
      +
manually written JSON schema
      +
explicit registry.register(...) call
```

The function name and parameters appear in several places and can become
inconsistent.

## Next chapters

The next question is: can Python inspect a function and generate its schema?

```text
06  Tool Registry
        ↓
07  Automatic Tool Schema
        ↓
08  @tool Decorator
```

Chapter 07 can use function signatures and type hints to generate JSON schemas.
Chapter 08 can then make registration convenient with a decorator. Keeping
these ideas separate makes it clear which problem each abstraction solves.
