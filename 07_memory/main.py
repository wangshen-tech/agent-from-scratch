import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from memory import Memory
from tools import registry


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


# 2. Use the same agent instructions as Chapter 06
SYSTEM_PROMPT = """
You are a helpful assistant.
You have several tools available. Choose the appropriate tool whenever you
need information or need to perform a calculation. You may call multiple tools
if the user's request requires them. After receiving the tool results, use them
to give the user a clear final answer. Weather results are demo data, not live
data, so always say that clearly.
""".strip()


# 3. Move conversation state into a reusable memory component
memory = Memory()

MAX_TOOL_ROUNDS = 5


# 4. Keep using the same agent loop as Chapter 06
def run_agent(user_input: str) -> str:
    memory.add_user_message(user_input)

    for tool_round in range(1, MAX_TOOL_ROUNDS + 1):
        print(f"\n[Agent step {tool_round}]")

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *memory.get_context(),
            ],
            tools=registry.get_schemas(),
        )

        assistant_message = response.choices[0].message
        memory.add_response(assistant_message)

        # No tool call means the agent has produced its final answer.
        if not assistant_message.tool_calls:
            return assistant_message.content or ""

        # The model may choose one tool or several tools in the same round.
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name

            try:
                tool_arguments = json.loads(tool_call.function.arguments)
                tool_result = registry.execute(
                    name=tool_name,
                    arguments=tool_arguments,
                )
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
                tool_arguments = {}
                tool_result = json.dumps({"error": str(error)})

            print(f"[Tool call] {tool_name}({tool_arguments})")
            print(f"[Tool result] {tool_result}")

            memory.add_tool_result(
                call_id=tool_call.id,
                result=tool_result,
            )

    limit_message = (
        f"I stopped after {MAX_TOOL_ROUNDS} tool rounds to avoid an infinite loop."
    )
    memory.add_response({"role": "assistant", "content": limit_message})
    return limit_message


# 5. Command-line chat loop
def main():
    print("=" * 55)
    print(f"Agent with Memory — {PROVIDER} / {MODEL}")
    print("Available tools:")
    print("  - get_weather")
    print("  - calculate")
    print("  - get_city_info")
    print()
    print("Commands:")
    print("  /memory  - show memory size")
    print("  /clear   - clear memory")
    print("  exit     - stop")
    print("=" * 55)

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if user_input == "/clear":
            memory.clear()
            print("Memory cleared.")
            continue

        if user_input == "/memory":
            print(f"Memory contains {len(memory)} items.")
            continue

        if not user_input:
            continue

        try:
            answer = run_agent(user_input)
            print(f"\nAssistant: {answer}")
        except Exception as error:
            print(f"\nError: {error}")


if __name__ == "__main__":
    main()
