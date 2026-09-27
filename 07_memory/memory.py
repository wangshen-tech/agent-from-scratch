class Memory:
    """Store short-term conversation context for the current process."""

    def __init__(self):
        self.items = []

    def add_user_message(self, content: str):
        """Store a message from the user."""
        self.items.append(
            {
                "role": "user",
                "content": content,
            }
        )

    def add_response(self, response_message):
        """Store one assistant message returned by the model."""
        self.items.append(response_message)

    def add_tool_result(self, call_id: str, result: str):
        """Store a tool result so the model can use it on the next step."""
        self.items.append(
            {
                "role": "tool",
                "tool_call_id": call_id,
                "content": result,
            }
        )

    def get_context(self):
        """Return everything currently stored in memory."""
        return self.items

    def clear(self):
        """Remove all stored conversation context."""
        self.items.clear()

    def __len__(self):
        return len(self.items)
