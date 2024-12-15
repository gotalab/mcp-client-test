import json
import re
import os
from typing import Optional
from dotenv import load_dotenv

from openai import OpenAI, AsyncOpenAI

class OpenAIAgent:
    def __init__(
        self,
        model_id: str = "gpt-4o",
        openai_api_key: Optional[str] = None,
        system_prompt: str = 'You are a helpful assistant.',
        max_tool_invocations: int = 5
    ):
        load_dotenv()
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API key must be provided either through constructor argument "
                "or environment variable 'OPENAI_API_KEY'"
            )
            
        self.model_id = model_id
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.system_prompt = system_prompt
        
        # 初期化時にsystemメッセージを設定
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        self.tools = None
        self.response_output_tags = []

        self.max_tool_invocations = max_tool_invocations
        self.tool_invocation_count = 0

    def set_system_prompt(self, prompt: str):
        """Systemプロンプトを変更し、メッセージ履歴をリセットする"""
        self.system_prompt = prompt
        self.messages = [
            {"role": "system", "content": self.system_prompt}
        ]

    async def invoke_with_prompt(self, prompt: str):
        """ユーザーからの新たなプロンプトに応答する"""
        self.messages.append({"role": "user", "content": prompt})
        return await self.invoke()

    async def get_response(self):
        """OpenAI APIにクエリを送り、completionを取得する関数"""
        params = {
            "model": self.model_id,
            "messages": self.messages,
        }
        
        # toolsが設定されている場合のみパラメータに追加
        if self.tools:
            tools = self.tools.get_tools()
            if tools:  # toolsが空でない場合のみ追加
                params["tools"] = tools
                params["tool_choice"] = "auto"
        
        completion = await self.client.chat.completions.create(**params)
        return completion


    async def invoke(self):
        if self.tool_invocation_count > self.max_tool_invocations:
            # ツール呼び出し回数の上限に達したら終了
            return "Tool invocation limit exceeded. Stopping to prevent infinite loop."

        completion = await self.get_response()
        choice = completion.choices[0]
        message = choice.message
        finish_reason = choice.finish_reason
        assistant_content = message.content

        # 必要ならレスポンスタグ処理
        if self.response_output_tags and len(self.response_output_tags) == 2:
            pattern = f"(?s).*{re.escape(self.response_output_tags[0])}(.*?){re.escape(self.response_output_tags[1])}"
            match = re.search(pattern, assistant_content)
            if match:
                assistant_content = match.group(1)

        self.messages.append({
            "role": "assistant",
            "content": assistant_content,
            "tool_calls": message.tool_calls if hasattr(message, 'tool_calls') else None
        })

        # ツール呼び出しがある場合
        if finish_reason == "tool_calls":
            self.tool_invocation_count += 1

            tool_calls = message.tool_calls or []
            for call in tool_calls:
                func_info = call.function
                func_name = func_info.name
                arguments_str = func_info.arguments
                arguments = json.loads(arguments_str)
                tool_use_id = call.id

                # payload = {
                #     "toolUseId": tool_use_id,
                #     "name": func_name,
                #     "input": arguments
                # }

                # ツール実行
                # tool_result = await self.tools.execute_tool(payload)
                tool_result = await self.tools.execute_tool(func_name, arguments)
                # ツール結果をtoolロールメッセージとして履歴にコミット
                function_call_result_message = {
                    "role": "tool",
                    "content": json.dumps(tool_result),
                    "tool_call_id": tool_use_id
                }
                print(function_call_result_message)
                self.messages.append(function_call_result_message)

            # ツール使用結果を反映させるため再度モデルに問い合わせ
            return await self.invoke()

        return assistant_content if assistant_content else ""

# import asyncio
# from typing import Optional

# async def main():
#     # OpenAIAgentのインスタンス作成
#     agent = OpenAIAgent(
#         model_id="gpt-4o",  # モデルIDを指定
#         system_prompt="You are a helpful assistant that provides clear and concise answers."
#     )
    
#     try:
#         # テスト用のプロンプト
#         test_prompt = "Please choose three expensive products."
        
#         # エージェントを呼び出し
#         response = await agent.invoke_with_prompt(test_prompt)
#         print(f"Response: {response}")
        
#     except Exception as e:
#         print(f"Error occurred: {e}")

# if __name__ == "__main__":
#     # asyncio.run()を使用してメインの非同期関数を実行
#     asyncio.run(main())