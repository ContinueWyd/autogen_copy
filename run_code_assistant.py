import asyncio
import os
from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo


async def main():
    # 1. 模型客户端
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

    # 2. 本地代码执行器
    executor = LocalCommandLineCodeExecutor(
        work_dir="code_exec_tmp",
        timeout=10,
    )

    # 3. writer：写代码
    writer = AssistantAgent(
        name="writer",
        model_client=model_client,
        system_message=(
            "你是一个 Python 程序员。"
            "根据用户需求写出代码，用 ```python 代码块包裹。"
            "写完后不要解释太多，让 executor 去执行。"
            "如果你确认代码输出正确，请在回复里加上 TERMINATE。"
        ),
    )

    # 4. executor：执行代码
    executor_agent = CodeExecutorAgent(
        name="executor",
        code_executor=executor,
    )

    # 5. 组成 Team：writer 先写，executor 执行
    team = RoundRobinGroupChat(
        participants=[writer, executor_agent],
        termination_condition=TextMentionTermination("TERMINATE")|MaxMessageTermination(10)
    )

    # 6. 跑任务
    task = """请执行以下代码，如果输出不对就修复它：

    ```python
    def sum_of_squares(n):
        return sum(i*i for i in range(1, n))

    print(sum_of_squares(3))
    ```
    """
    result = await team.run(task=task)

    # 7. 打印消息流
    for i, msg in enumerate(result.messages):
        print(f"--- 第 {i} 条 ---")
        print(f"类型: {type(msg).__name__}")
        print(f"来源: {msg.source}")
        print(f"内容: {msg.content}\n")


if __name__ == "__main__":
    asyncio.run(main())