import asyncio
import os
from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
from autogen_agentchat.teams import RoundRobinGroupChat, Swarm
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

    # 3. writer：写代码 / 修正代码，写完交给 executor
    writer = AssistantAgent(
        name="writer",
        model_client=model_client,
        system_message=(
            "你是一个 Python 程序员。"
            "根据用户需求或 verifier 的意见写代码/修正代码，用 ```python 代码块包裹。"
            "写完后，把任务交给 executor 执行。"
        ),
        handoffs=["executor"],
    )

    # 4. executor：执行代码，执行完交给 verifier
    executor_agent = CodeExecutorAgent(
        name="executor",
        code_executor=executor,
        handoffs=["verifier"],
    )

    # 5. verifier：验证执行结果，通过说 TERMINATE，不通过交回 writer
    verifier = AssistantAgent(
        name="verifier",
        model_client=model_client,
        system_message=(
            "你是一个验证员。检查 executor 的执行结果是否正确。"
            "如果正确，回复 '验证通过' 并加上 TERMINATE。"
            "如果不正确，指出具体问题，并把任务交回给 writer。"
            "不要自己写代码。"
        ),
        handoffs=["writer"],
    )

    # 6. Swarm：Agent 自己决定移交给谁
    team = Swarm(
        participants=[writer, executor_agent, verifier],
        termination_condition=(
                TextMentionTermination("TERMINATE") | MaxMessageTermination(15)
        ),
    )

    # 7. 跑任务
    task = """请执行以下代码，如果输出不对就修复它：

    ```python
    def sum_of_squares(n):
        return sum(i*i for i in range(1, n))

    print(sum_of_squares(3))
    ```
    """
    result = await team.run(task=task)

    # 8. 打印消息流
    for i, msg in enumerate(result.messages):
        print(f"--- 第 {i} 条 ---")
        print(f"类型: {type(msg).__name__}")
        print(f"来源: {msg.source}")
        print(f"内容: {msg.content}\n")


if __name__ == "__main__":
    asyncio.run(main())