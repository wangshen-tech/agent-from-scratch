# 01 — Simple Agent

This chapter builds the smallest multi-model chat program:

```text
User → selected model → answer
```

It has a `while` loop, so you can ask multiple questions. However, every API request contains only the current question, so the model does not remember earlier turns.

## Configure it

Edit the project `.env` file:

```ini
PROVIDER=deepseek
API_KEY=your_api_key
MODEL=deepseek-flash
```

| `PROVIDER` | Example `MODEL` |
|---|---|
| `openai` | `gpt-5.6` |
| `deepseek` | `deepseek-flash` |
| `claude` | `claude-sonnet-4-6` |
| `glm` | `glm-5-turbo` |

The API key and model must belong to the selected provider.

## Run it

```bash
cd ~/Desktop/agent-from-scratch
source .venv/bin/activate
python 01_simple_agent/main.py
```

Try telling the model your name and then asking for it:

```text
You: My name is Alex.
Assistant: Nice to meet you, Alex!

You: What is my name?
```

The model receives only `What is my name?`, so it cannot reliably know the answer. Chapter 02 fixes this by storing conversation history.
