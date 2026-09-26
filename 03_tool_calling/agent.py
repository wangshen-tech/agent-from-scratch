import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from tools import AVAILABLE_TOOLS, TOOLS


# 1. Load the same settings used in earlier chapters
load_dotenv()

PROVIDER = os.getenv("PROVIDER", "deepseek").lower()
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")

BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "deepseek": "https://api.deepseek.com",
    "claude": "https://api.anthropic.com/v1/",
    "glm": "https://open.bigmodel.cn/api/paas/v4",
}

if PROVIDER not in BASE_URLS:
    raise ValueError("PROVIDER must be: openai, deepseek, claude, or glm")

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URLS[PROVIDER],
)


# 2. Store the conversation
SYSTEM_PROMPT = """
You are a helpful assistant.
Use get_weather whenever the user asks about weather.
Always explain that the weather result is demo data, not live data.
""".strip()

messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]


# 3. Send one user message through the agent
def run_agent(user_input):
    messages.append({"role": "user", "content": user_input})

    # First model call: answer directly or request a tool.
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
    )

    assistant_message = response.choices[0].message
    messages.append(assistant_message)

    # No tool call means the model already produced the final answer.
    if not assistant_message.tool_calls:
        return assistant_message.content

    # Execute every tool requested by the model.
    for tool_call in assistant_message.tool_calls:
        tool_name = tool_call.function.name
        tool_arguments = json.loads(tool_call.function.arguments)
        tool_function = AVAILABLE_TOOLS.get(tool_name)

        if tool_function:
            tool_result = tool_function(**tool_arguments)
        else:
            tool_result = {"error": f"Unknown tool: {tool_name}"}

        # Send the Python function result back to the model.
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result),
            }
        )

    # Second model call: turn the tool result into a natural-language answer.
    final_response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
    )

    final_message = final_response.choices[0].message
    messages.append(final_message)
    return final_message.content


# 4. Command-line chat loop
print(f"Using {PROVIDER} / {MODEL}")
print("Tool calling is on. Type 'exit' to stop.")

while True:
    user_input = input("\nYou: ").strip()

    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    if not user_input:
        continue

    answer = run_agent(user_input)
    print(f"Assistant: {answer}")
