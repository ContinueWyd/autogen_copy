
"""
A1: 多 Agent 代码助手

writer 写代码 → tester 测试 → verifier 审查
编排方式：Swarm

详见 README.md
"""

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
            "写代码后，用 execute_python_code 工具执行它。"
            "执行成功后，在回复里用 ```python 代码块贴出完整代码，"
            "然后把任务交给 tester。"
        ),
        tools=[execute_tool],
        handoffs=["tester"],
    )

    tester = AssistantAgent(
        name="tester",
        model_client=model_client,
        system_message=(
            "你是一个测试工程师。"
            "针对 writer 的代码，设计 5-10 个测试用例（含边界）。"
            "用 execute_python_code 工具执行测试。"
            "测试完成后，在回复里用 ```python 代码块贴出完整代码和测试结果，"
            "然后把任务交给 verifier。"
        ),
        tools=[execute_tool],  # tester 也能调执行工具
        handoffs=["writer", "verifier"],  # 可以交回 writer，也可以交给 verifier
    )

    # 5. verifier：验证最终结果
    verifier = AssistantAgent(
        name="verifier",
        model_client=model_client,
        system_message=(
            "你是一个验证员。你会收到 writer 和 tester 的完整代码与测试结果。"
            "请直接检查代码本身："
            "1. 代码逻辑是否正确（逐行审查）"
            "2. 测试覆盖是否充分（是否漏测关键边界）"
            "3. 有没有潜在 bug（比如边界、类型、异常）"
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
    # ============================================================
    # 示例任务：可替换成任意编程题
    # ============================================================
    # 7. 跑任务
    task = """写一个 Python 函数 is_match(s, p)，实现正则表达式匹配，支持 '.' 和 '*'。

    规则：
    1. '.' 匹配任意单个字符。
    2. '*' 匹配零个或多个前面的那一个元素。
    3. 匹配必须覆盖整个字符串 s，而不是部分匹配。

    测试用例：
    - is_match("aa", "a") → False
    - is_match("aa", "a*") → True
    - is_match("ab", ".*") → True
    - is_match("aab", "c*a*b") → True
    - is_match("mississippi", "mis*is*p*.") → False
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