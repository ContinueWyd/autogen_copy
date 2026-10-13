import asyncio
import os
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import MagenticOneGroupChat
from autogen_core.models import ModelInfo

async def main():
    model_client = OpenAIChatCompletionClient(
        model="deepseek-v4-flash",
        base_url="https://www.micuapi.ai/v1",
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        model_info=ModelInfo(
            vision=False,
            function_calling=True,
            json_output=True,
            structured_output=False,
            family="unknown",
        ),
    )

    # 只需要一个基础 Agent 就能跑，Orchestrator 是内置的
    assistant = AssistantAgent(
        name="assistant",
        model_client=model_client,
        system_message="你是一个助手，请一步步解决用户的问题。",
    )

    team = MagenticOneGroupChat(
        [assistant],
        model_client=model_client,
        max_turns=10,
    )

    result = await team.run(task="用一句话解释什么是 Agent。")
    for i, msg in enumerate(result.messages):
        print(f"--- 第 {i} 条 ---")
        print(f"类型: {type(msg).__name__}")
        print(f"来源: {msg.source}")
        print(f"内容: {msg.content}\n")

if __name__ == "__main__":
    asyncio.run(main())