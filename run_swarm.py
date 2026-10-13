import asyncio
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import Swarm
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

    # 分流 Agent：根据问题类型，把任务移交给对应的专家
    triage = AssistantAgent(
        name="triage",
        model_client=model_client,
        description="负责判断问题类型，并移交给对应的专家。",
        system_message=(
            "你是问题分流员。"
            "如果用户问的是代码问题，把任务移交给 coder。"
            "如果用户问的是天气问题，把任务移交给 weather_expert。"
            "移交时，在你的回复里明确说出对方的名称。"
        ),
        handoffs=["coder", "weather_expert"],   # 关键：告诉它可以把任务交给谁
    )

    coder = AssistantAgent(
        name="coder",
        model_client=model_client,
        description="解决代码问题。",
        system_message="你是程序员，负责回答代码问题。回答完说 TERMINATE。",
        handoffs=["triage"],   # 也可以交回给 triage
    )

    weather_expert = AssistantAgent(
        name="weather_expert",
        model_client=model_client,
        description="回答天气问题。",
        system_message="你负责回答天气问题。回答完说 TERMINATE。",
        handoffs=["triage"],
    )

    team = Swarm(
        participants=[triage, coder, weather_expert],
        termination_condition=TextMentionTermination("TERMINATE"),
    )

    result = await team.run(task="帮我写一个 Python 函数，计算两个数的和。")

    for i, msg in enumerate(result.messages):
        print(f"--- 第 {i} 条 ---")
        print(f"类型: {type(msg).__name__}")
        print(f"来源: {msg.source}")
        print(f"内容: {msg.content}\n")


if __name__ == "__main__":
    asyncio.run(main())