# 02 — Conversation

Chapter 01 sends only the latest user message:

```text
User → LLM → answer
```

This chapter adds one new concept: **conversation history**.

```text
             conversation history
                      │
                      ▼
User → messages → LLM → answer
          ▲             │
          └─────────────┘
```

## How memory works

An API request is independent from earlier requests. To give the model context, the program stores earlier messages in a Python list:

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."}
]
```

When the user types a message, it is added to the list:

```python
messages.append({"role": "user", "content": user_input})
```

The whole list is sent to the model:

```python
response = client.chat.completions.create(
    model=MODEL,
    messages=messages,
)
```

The assistant's answer is also saved:

```python
messages.append({"role": "assistant", "content": answer})
```

After several turns, the list looks like this:

```python
[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "My name is Shen."},
    {"role": "assistant", "content": "Nice to meet you, Shen!"},
    {"role": "user", "content": "What is my name?"},
]
```

Because the earlier messages are sent again, the model can answer the final question using that context.

## Run it

The program uses the same `.env` configuration as Chapter 01:

```bash
cd ~/Desktop/agent-from-scratch
source .venv/bin/activate
python 02_conversation/main.py
```

Try:

```text
You: My name is Shen.
Assistant: Nice to meet you, Shen!

You: I am studying applied mathematics.
Assistant: That's great!

You: What am I studying?
Assistant: You are studying applied mathematics.
```

Type `exit` to stop.

## What kind of memory is this?

This is short-term, in-process memory:

- It exists only while the program is running.
- It disappears when the program stops.
- The entire history is sent again on every request.

There is no database, memory class, vector store, or framework yet. Those can be introduced later when this simple list becomes insufficient.
