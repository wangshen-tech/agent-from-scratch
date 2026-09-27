# 04 — Agent Loop

Chapter 03 can handle one round of tool calls. That is enough for a simple
question, but some tasks need the result of one tool before the model knows
how to call the next tool.

Chapter 04 adds one new concept: an **agent loop**.

```text
                     ┌──────────────────────┐
                     │                      │
                     ▼                      │
User → messages → model → tool call → Python function
                     │                      │
                     │          tool result ┘
                     │
                     └─ no tool call → final answer
```

## Project structure

```text
04_agent_loop/
├── README.md
├── agent.py
└── tools.py
```

- `tools.py` contains two Python functions and their JSON schemas.
- `agent.py` runs tools and keeps calling the model until the task is done.

## Why one tool round is not always enough

Suppose the user asks:

```text
What is the demo weather in Toronto? Give the temperature in Fahrenheit.
```

The model should not guess the Celsius temperature. It needs to:

1. Call `get_weather(location="Toronto")`.
2. Read `temperature_c` from the result.
3. Call `celsius_to_fahrenheit(celsius=22)`.
4. Use both results to write the final answer.

The second tool call depends on the first tool result, so the program must
return control to the model after every tool round.

## The agent loop

The core of this chapter is a loop around the model call:

```python
for tool_round in range(1, MAX_TOOL_ROUNDS + 1):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
    )

    assistant_message = response.choices[0].message
    messages.append(assistant_message)

    if not assistant_message.tool_calls:
        return assistant_message.content

    for tool_call in assistant_message.tool_calls:
        tool_message = execute_tool_call(tool_call, tool_round)
        messages.append(tool_message)
```

Each pass has two possible outcomes:

- If the model requests tools, Python executes them and the loop continues.
- If the model requests no tools, its text is the final answer and the loop stops.

This repeated **model → action → observation** cycle is the basic control flow
behind many agents.

## Why there is a round limit

A model can make a mistake and repeatedly request tools. The constant below
prevents an infinite loop:

```python
MAX_TOOL_ROUNDS = 5
```

Production agents often add more controls, such as timeouts, token budgets,
tool permissions, argument validation, and human approval for risky actions.

## Run it

Use the same root `.env` file as the earlier chapters. The selected model must
support OpenAI-compatible tool calling.

```bash
cd ~/Desktop/agent-from-scratch
source .venv/bin/activate
python 04_agent_loop/agent.py
```

On Windows PowerShell, after activating your environment, run:

```powershell
python .\04_agent_loop\agent.py
```

Try a task that needs two dependent tool calls:

```text
You: What is the demo weather in Toronto? Give the temperature in Fahrenheit.

[Tool round 1] get_weather({'location': 'Toronto'})
[Tool result] {'location': 'Toronto', 'temperature_c': 22, ...}

[Tool round 2] celsius_to_fahrenheit({'celsius': 22})
[Tool result] {'celsius': 22, 'fahrenheit': 71.6}

Assistant: The demo weather in Toronto is sunny and 71.6°F. This is demo data,
not live weather.
```

Also try a question that needs no tool:

```text
You: Explain an agent loop in one sentence.
```

## What changed from Chapter 03?

| Chapter 03 | Chapter 04 |
|---|---|
| One model call after tool results | Repeats until there are no tool calls |
| One demo tool | Two tools that can be chained |
| Tool execution is inside `run_agent()` | Tool execution has its own reusable function |
| No loop limit is needed | Stops after at most five tool rounds |

## Current limitations

- The weather is still fake demonstration data.
- Conversation history exists only while the program is running.
- Tool calls are executed automatically without user approval.
- The loop has a round limit, but no token or cost budget.
- Tool results are sent directly to the model without trust or safety checks.
