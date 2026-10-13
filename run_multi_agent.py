import asyncio
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo


async def main():
    # 1. 配置模型客户端（和单 Agent 一样，可复用）
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

    # 2. 创建两个 Agent：一个写代码，一个审查
    writer = AssistantAgent(
        name="writer",
        model_client=model_client,
        system_message=(
            "你是一个 Python 程序员。"
            "根据用户需求写出简洁、可运行的代码。"
            "只输出代码和必要的解释，不要啰嗦。"
        ),
    )

    reviewer = AssistantAgent(
        name="reviewer",
        model_client=model_client,
        system_message=(
            "你是一个严格的代码审查员。"
            "检查 writer 写的代码：逻辑是否正确、边界情况是否处理、命名是否清晰。"
            "如果有问题，指出具体问题并给出修改建议。"
            "如果代码没问题，回复'代码通过审查'并附上 TERMINATE。"
        ),
    )

    # 3. 组成一个团队，让它们轮流发言
    # 终止条件：看到 TERMINATE 就停，或最多 10 条消息
    termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(10)
    team = RoundRobinGroupChat(
        participants=[writer, reviewer],
        termination_condition= termination ,  # 最多 6 条消息，防止无限循环
    )

    # 4. 跑任务
    task = "写一个 Python 函数，计算斐波那契数列的第 n 项。"
    result = await team.run(task=task)

    # 5. 打印完整消息流
    for i, msg in enumerate(result.messages):
        print(f"--- 第 {i} 条 ---")
        print(f"类型: {type(msg).__name__}")
        print(f"来源: {msg.source}")
        print(f"内容: {msg.content}")
        print()


if __name__ == "__main__":
    asyncio.run(main())