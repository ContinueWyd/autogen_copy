import asyncio
from autogen_agentchat.agents import CodeExecutorAgent
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor


async def main():
    # 1. 创建本地代码执行器
    #    所有代码都会在 work_dir 目录里执行
    executor = LocalCommandLineCodeExecutor(
        work_dir="code_exec_tmp",   # 相对路径，会在项目下新建这个目录
        timeout=10,                 # 单次执行超时 10 秒
    )

    # 2. 创建 CodeExecutorAgent
    #    注意：它不需要 model_client
    code_agent = CodeExecutorAgent(
        name="code_executor",
        code_executor=executor,
    )

    # 3. 准备任务：里面包含要执行的代码块
    task = """请执行以下 Python 代码：

```python
print("Hello from CodeExecutorAgent")
print(1 + 1)
print([i**2 for i in range(5)])
```
"""

    # 4. 执行
    result = await code_agent.run(task=task)

    # 5. 打印消息流
    for i, msg in enumerate(result.messages):
        print(f"--- 第 {i} 条 ---")
        print(f"类型: {type(msg).__name__}")
        print(f"来源: {msg.source}")
        print(f"内容: {msg.content}\n")


if __name__ == "__main__":
    asyncio.run(main())