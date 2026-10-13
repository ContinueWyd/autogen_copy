import asyncio
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination
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

    # 两个 Agent，各自有 description，供选择器判断
    writer = AssistantAgent(
        name="writer",
        model_client=model_client,
        description="写 Python 代码的程序员。",
        system_message="你是一个 Python 程序员。根据用户需求写出简洁、可运行的代码。",
    )

    reviewer = AssistantAgent(
        name="reviewer",
        model_client=model_client,
        description="审查代码的审查员。",
        system_message=(
            "你是一个严格的代码审查员。检查 writer 的代码逻辑、边界、命名。"
            "如果代码没问题，回复'代码通过审查'并附上 TERMINATE。"
        ),
    )

    # 关键区别：用 model_client 来决定下一个谁发言
    team = SelectorGroupChat(
        participants=[writer, reviewer],
        model_client=model_client,
        termination_condition=TextMentionTermination("TERMINATE"),
    )

    result = await team.run(task="写一个 Python 函数，计算斐波那契数列的第 n 项。")

    for i, msg in enumerate(result.messages):
        print(f"--- 第 {i} 条 ---")
        print(f"类型: {type(msg).__name__}")
        print(f"来源: {msg.source}")
        print(f"内容: {msg.content}\n")


if __name__ == "__main__":
    asyncio.run(main())