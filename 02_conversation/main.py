import os

from dotenv import load_dotenv
from openai import OpenAI


# 1. Load the same settings used in Chapter 01
load_dotenv()

PROVIDER = os.getenv("PROVIDER", "deepseek").lower()
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")


# 2. Choose the API address for the selected provider
BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "deepseek": "https://api.deepseek.com",
    "claude": "https://api.anthropic.com/v1/",
    "glm": "https://open.bigmodel.cn/api/paas/v4",
}

if PROVIDER not in BASE_URLS:
    raise ValueError("PROVIDER must be: openai, deepseek, claude, or glm")


# 3. Create the model client
client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URLS[PROVIDER],
)


# 4. NEW: Store the conversation in a Python list
messages = [
    {"role": "system", "content": "You are a helpful assistant."}
]


# 5. Keep chatting until the user exits
print(f"Using {PROVIDER} / {MODEL}")
print("Conversation memory is on. Type 'exit' to stop.")

while True:
    user_input = input("\nYou: ").strip()

    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    if not user_input:
        continue

    # Save the user's new message.
    messages.append({"role": "user", "content": user_input})

    # Send the entire conversation to the model.
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )

    answer = response.choices[0].message.content
    print(f"Assistant: {answer}")

    # Save the answer for the next turn.
    messages.append({"role": "assistant", "content": answer})
