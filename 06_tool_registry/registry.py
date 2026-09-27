class ToolRegistry:
    """Store tool functions and the JSON schemas sent to the model."""

    def __init__(self):
        # Maps a tool name to the Python function that implements it.
        self.functions = {}

        # Stores the schemas that describe the tools to the model.
        self.schemas = []

    def register(self, name: str, function, schema: dict):
        """Register one function and its manually written schema."""
        if name in self.functions:
            raise ValueError(f"Tool '{name}' is already registered.")

        self.functions[name] = function
        self.schemas.append(schema)

    def get_schemas(self) -> list:
        """Return all schemas that should be sent to the model."""
        return self.schemas

    def execute(self, name: str, arguments: dict) -> str:
        """Find a registered function by name and execute it."""
        if name not in self.functions:
            raise ValueError(f"Unknown tool: {name}")

        function = self.functions[name]
        return function(**arguments)
