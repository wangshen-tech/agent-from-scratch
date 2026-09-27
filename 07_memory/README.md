# 07 — Memory

Chapter 02 already introduced conversation history with a Python list. The
agent could remember earlier messages because the entire list was sent to the
model again on every request.

Chapter 07 does not introduce memory as a completely new capability. It adds
one architectural idea: move conversation history out of `main.py` and make it
a reusable **Memory component**.

```text
Before                          After

main.py                         Agent
├── agent loop                   ├── Agent Loop
├── model calls                  ├── Tool Registry
├── tool results                 └── Memory
└── messages list                    └── conversation state
```

This chapter implements short-term, in-process memory only. It does not use a
database, vector database, RAG, or long-term storage.

## Project structure

```text
07_memory/
├── README.md
├── main.py
├── memory.py
├── registry.py
└── tools.py
```

Only `memory.py` introduces a new component. The provider configuration, agent
loop, tool registry, three tools, and manually written schemas remain the same
as Chapter 06.

## From a list to a component

Chapter 06 stored conversation state directly in `main.py`:

```python
messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]
```

The agent loop then called `messages.append(...)` in several places.

Chapter 07 creates a memory object instead:

```python
memory = Memory()
```

The loop communicates through a small interface:

```python
memory.add_user_message(user_input)
memory.add_response(assistant_message)
memory.add_tool_result(call_id, result)
memory.get_context()
memory.clear()
```

The underlying storage is still a normal Python list. The important change is
that `Memory`, rather than `main.py`, now owns it.

## The `Memory` class

The class starts with an empty list:

```python
class Memory:
    def __init__(self):
        self.items = []
```

It stores each part of the conversation in the order it happens.

### User messages

```python
def add_user_message(self, content):
    self.items.append(
        {
            "role": "user",
            "content": content,
        }
    )
```

### Assistant responses

The complete assistant message is stored because it may contain text or tool
calls:

```python
def add_response(self, response_message):
    self.items.append(response_message)
```

### Tool results

A tool result must include the matching call ID:

```python
def add_tool_result(self, call_id, result):
    self.items.append(
        {
            "role": "tool",
            "tool_call_id": call_id,
            "content": result,
        }
    )
```

That lets the model connect the result to the tool call it requested.

## Memory inside the agent loop

The new flow is:

```text
                ┌────────────────────────┐
                │                        │
                ▼                        │
User → Memory → LLM → Tool → Memory ─────┘
                │
                │ no tool call
                ▼
             Answer
```

First, the user message enters memory:

```python
memory.add_user_message(user_input)
```

The model receives the system instruction followed by everything currently in
memory:

```python
messages=[
    {"role": "system", "content": SYSTEM_PROMPT},
    *memory.get_context(),
]
```

The system prompt is kept separate because `/clear` should erase the
conversation without removing the agent’s permanent instructions.

After the model responds, its message is stored:

```python
memory.add_response(assistant_message)
```

If it requested a tool, the result is stored too:

```python
memory.add_tool_result(
    call_id=tool_call.id,
    result=tool_result,
)
```

The next loop iteration receives all this context and can continue from the
previous step.

## Conversation history versus a Memory component

The underlying behavior is related, but the teaching goals differ:

| Chapter | Main lesson |
|---|---|
| 02 — Conversation | Why earlier messages must be sent back to the model |
| 07 — Memory | How conversation state becomes an independent component |

For this small program, a list in `main.py` would still work. The component
becomes valuable when memory later needs additional behavior such as:

- limiting context size
- removing old messages
- summarizing earlier conversation
- saving and loading conversations
- retrieving only relevant information

Those changes can be made inside `Memory` without rewriting the agent loop.

## What is stored?

Memory contains more than user text. A tool conversation may look like:

```text
User message
    ↓
Assistant tool call
    ↓
Tool result
    ↓
Assistant final answer
```

Every item is needed for valid context on later model calls.

For example, after asking for Toronto’s weather, the user can ask:

```text
What temperature did you just tell me?
```

The agent can answer because memory contains the earlier question, tool call,
tool result, and final response.

## Inspecting and clearing memory

The CLI includes two commands for demonstrating the component.

Enter:

```text
/memory
```

to display the number of stored items:

```text
Memory contains 4 items.
```

One item is not always one conversation turn. User messages, assistant
responses, tool calls, and tool results can each contribute stored context.

Enter:

```text
/clear
```

to erase the current conversation. The system prompt and tool definitions are
not conversation memory, so they remain available.

## Run it

Use the same root `.env` configuration as the earlier chapters. The selected
model must support OpenAI-compatible tool calling.

From the project root:

```bash
python 07_memory/main.py
```

On Windows PowerShell:

```powershell
python .\07_memory\main.py
```

Try ordinary conversation memory:

```text
You: My name is Shen.
You: I am studying applied mathematics.
You: What is my name and what am I studying?
```

Then test memory containing a tool call:

```text
You: What is the weather in Toronto?
You: What temperature did you just tell me?
```

Finally, inspect and clear it:

```text
/memory
/clear
/memory
```

## Short-term memory only

The current memory exists only in RAM:

```text
program starts → Memory() creates an empty list
program exits  → the list disappears
```

If you tell the agent something, close the program, and start it tomorrow, the
agent will not remember it. Nothing is saved to disk.

This is not persistent or long-term memory. Later implementations could use a
JSON file, SQLite, another database, summaries, or retrieval, but those are
outside this chapter.

## Current limitation

`Memory` keeps appending items forever. A very long conversation would become
slow, expensive, and eventually exceed the model’s context window.

Possible future strategies include keeping only recent messages, summarizing
old messages, and retrieving only relevant memories. Chapter 07 deliberately
does not implement those strategies yet.

## What we have built

```text
01  Simple model call
02  Raw conversation history
03  Tool calling
04  Agent loop
05  Multiple tools
06  Tool registry
07  Reusable memory component
```

The important distinction is:

```text
02 teaches why conversation history is needed.
07 teaches how memory becomes an independent agent component.
```
