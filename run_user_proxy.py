import asyncio
import os
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
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

    # 1. AssistantAgent：负责回答
    assistant = AssistantAgent(
        name="assistant",
        model_client=model_client,
        system_message="你是一个有用的助手。回答完请说 TERMINATE。",
    )

    # 2. UserProxyAgent：代表用户发言
    user_proxy = UserProxyAgent(
        name="user_proxy",
    )

    # 3. 组成 Team：user_proxy 先发言，assistant 回应
    team = RoundRobinGroupChat(
        participants=[user_proxy, assistant],
        termination_condition=MaxMessageTermination(4),
    )

    result = await team.run(task="用一句话解释什么是 Agent。")

    for i, msg in enumerate(result.messages):
        print(f"--- 第 {i} 条 ---")
        print(f"类型: {type(msg).__name__}")
        print(f"来源: {msg.source}")
        print(f"内容: {msg.content}\n")


if __name__ == "__main__":
    asyncio.run(main())