from typing import Any, Dict, List, Callable

class OpenAIToolManager:
    def __init__(self):
        """
        OpenAIのassistant作成時に渡す`tools`（functions）形式のリストを管理する
        """
        self._tools = {}
        self._name_mapping = {}

    def _sanitize_name(self, name: str) -> str:
        return name.replace('-', '_')

    def register_tool(self, name: str, func: Callable, description: str, input_schema: Dict):
        """
        ツールを登録する。
        input_schema: JSON Schema形式のproperties定義
        
        例:
        input_properties = {
            "location": {
                "type": "string",
                "description": "The city and state, e.g., San Francisco, CA"
            },
            "unit": {
                "type": "string",
                "enum": ["Celsius", "Fahrenheit"],
                "description": "The temperature unit"
            }
        }
        required_fields = ["location", "unit"]
        """
        
        sanitized_name = self._sanitize_name(name)
        self._name_mapping[sanitized_name] = name
        
        # Construct JSON Schema
        self._tools[sanitized_name] = {
            'function': func,
            'description': description,
            'input_schema': input_schema,
            'original_name': name
        }

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        OpenAIのassistant作成時に渡す`tools`（functions）形式のリストを返す
        """
        functions = []
        for sanitized_name, tool in self._tools.items():
            fn = {
                "type": "function",
                "function": {
                    "name": sanitized_name,
                    "description": tool['description'],
                    "parameters": tool['input_schema']
                }
            }
            functions.append(fn)
        return functions

    async def execute_tool(self, tool_name: str, arguments: dict) -> Dict[str, Any]:
        """
        MCPサーバ上のツールを実行。
        """
        if tool_name not in self._tools:
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            original_name = self._tools[tool_name]['original_name']
            tool_func = self._tools[tool_name]['function']
            result = await tool_func(original_name, arguments)  # mcp_client.call_toolを想定
            return {"content": str(result)}
        except Exception as e:
            return {"content": f"Error executing tool: {str(e)}"}

    def clear_tools(self):
        self._tools.clear()
        self._name_mapping.clear()