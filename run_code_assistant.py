import asyncio
import os
from autogen_agentchat.agents import AssistantAgent, CodeExecutorAgent
from autogen_agentchat.teams import RoundRobinGroupChat, Swarm
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_core import code_executor, CancellationToken
from autogen_core.code_executor import CodeBlock
from autogen_core.tools import FunctionTool
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

    # 3. 把"执行代码"包装成工具函数
    async def execute_python_code(code: str) -> str:
        """执行传入的 Python 代码，返回运行结果。

        Args:
            code: 要执行的 Python 代码字符串。
        """
        result = await executor.execute_code_blocks(
            code_blocks=[CodeBlock(code=code, language="python")],
            cancellation_token=CancellationToken(),
        )
        return result.output

    execute_tool = FunctionTool(
        execute_python_code,
        description="执行 Python 代码并返回结果。写完代码后调用它来验证。",
    )

    # 4. writer：写代码 + 持有执行工具
    writer = AssistantAgent(
        name="writer",
        model_client=model_client,
        system_message=(
            "你是一个 Python 程序员。"
            "写代码后，必须调用 execute_python_code 工具来执行它。"
            "确认基本正确后，把任务交给 tester 测试。"
        ),
        tools=[execute_tool],
        handoffs=["tester"],
    )

    tester = AssistantAgent(
        name="tester",
        model_client=model_client,
        system_message=(
            "你是一个测试工程师。"
            "针对 writer 写的代码，设计 3-5 个测试用例（包括边界情况）。"
            "用 execute_python_code 工具执行测试。"
            "如果测试通过，交给 verifier。"
            "如果测试失败，交回 writer 修正。"
        ),
        tools=[execute_tool],  # tester 也能调执行工具
        handoffs=["writer", "verifier"],  # 可以交回 writer，也可以交给 verifier
    )

    # 5. verifier：验证最终结果
    verifier = AssistantAgent(
        name="verifier",
        model_client=model_client,
        system_message=(
            "你是一个验证员。检查 writer 的代码和执行结果是否正确。"
            "如果正确，回复 '验证通过' 并加上 TERMINATE。"
            "如果不正确，指出具体问题，并把任务交回给 writer。"
        ),
        handoffs=["writer"],
    )

    # 6. Swarm
    team = Swarm(
        participants=[writer, tester,verifier],
        termination_condition=TextMentionTermination("TERMINATE") | MaxMessageTermination(20),
    )

    # 7. 跑任务
    task = """写一个 Python 函数 two_sum(nums, target)，找出列表 nums 中两个数，使它们的和等于 target，返回这两个数的下标。

    要求：
    1. 假设每个输入只有一个答案。
    2. 同一个元素不能重复使用。

    测试用例：
    - nums = [2, 7, 11, 15], target = 9 → 返回 [0, 1]
    - nums = [3, 2, 4], target = 6 → 返回 [1, 2]
    """
    result = await team.run(task=task)

    # 8. 打印消息流
    for i, msg in enumerate(result.messages):
        print(f"--- 第 {i} 条 ---")
        print(f"类型: {type(msg).__name__}")
        print(f"来源: {msg.source}")

        # 处理不同消息类型
        content = msg.content

        # 如果是列表（比如 ToolCallRequestEvent 里的 FunctionCall 列表）
        if isinstance(content, list):
            for item in content:
                # 如果有 code 参数，单独多行显示
                if hasattr(item, "arguments") and isinstance(item.arguments, str):
                    import json
                    try:
                        args = json.loads(item.arguments)
                        if "code" in args:
                            print(f"代码:\n{args['code']}")
                        else:
                            print(f"参数: {args}")
                    except Exception:
                        print(f"内容: {item}")
                else:
                    print(f"内容: {item}")
        else:
            print(f"内容: {content}")

        print()


if __name__ == "__main__":
    asyncio.run(main())