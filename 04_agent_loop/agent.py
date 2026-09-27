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


# 2. Give the agent rules for using tools
SYSTEM_PROMPT = """
You are a helpful assistant.
Use get_weather whenever the user asks about weather.
The weather tool returns demo data, not live data, so always say that clearly.
If the user wants a weather temperature in Fahrenheit, first call get_weather,
read temperature_c from its result, and then call celsius_to_fahrenheit.
Never invent a tool result.
""".strip()

messages = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

# Prevent a confused model from calling tools forever.
MAX_TOOL_ROUNDS = 5


# 3. Execute one tool call requested by the model
def execute_tool_call(tool_call, tool_round):
    tool_name = tool_call.function.name
    tool_function = AVAILABLE_TOOLS.get(tool_name)

    try:
        tool_arguments = json.loads(tool_call.function.arguments)
    except json.JSONDecodeError:
        tool_arguments = {}
        tool_result = {"error": "The tool arguments were not valid JSON."}
    else:
        if tool_function is None:
            tool_result = {"error": f"Unknown tool: {tool_name}"}
        else:
            try:
                tool_result = tool_function(**tool_arguments)
            except (TypeError, ValueError) as error:
                tool_result = {"error": str(error)}

    print(f"\n[Tool round {tool_round}] {tool_name}({tool_arguments})")
    print(f"[Tool result] {tool_result}")

    return {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": json.dumps(tool_result, ensure_ascii=False),
    }


# 4. Keep calling the model until it gives a final answer
def run_agent(user_input):
    messages.append({"role": "user", "content": user_input})

    for tool_round in range(1, MAX_TOOL_ROUNDS + 1):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
        )

        assistant_message = response.choices[0].message
        messages.append(assistant_message)

        # No tool call means the agent has finished the task.
        if not assistant_message.tool_calls:
            return assistant_message.content or ""

        # Run every tool requested in this round, then loop back to the model.
        for tool_call in assistant_message.tool_calls:
            tool_message = execute_tool_call(tool_call, tool_round)
            messages.append(tool_message)

    limit_message = (
        f"I stopped after {MAX_TOOL_ROUNDS} tool rounds to avoid an infinite loop."
    )
    messages.append({"role": "assistant", "content": limit_message})
    return limit_message


# 5. Command-line chat loop
def main():
    print(f"Using {PROVIDER} / {MODEL}")
    print("Agent loop is on. Type 'exit' to stop.")

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        if not user_input:
            continue

        answer = run_agent(user_input)
        print(f"Assistant: {answer}")


if __name__ == "__main__":
    main()
