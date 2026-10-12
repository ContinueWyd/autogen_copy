import asyncio
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo




async def main():
    model_client = OpenAIChatCompletionClient(
        model="deepseek-v4-flash",                          # 换成你的模型名
        base_url="https://www.micuapi.ai/v1",          # DeepSeek 的 OpenAI 兼容地址
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        model_info=ModelInfo(
            vision=False,  # DeepSeek 目前不支持图片输入
            function_calling=True,  # 支持工具/函数调用
            json_output=True,  # 支持 JSON 格式输出（或 structured_output）
            structured_output=False,  # 加上这行
            family="unknown",  # 模型家族，非 OpenAI 模型统一用 unknown
        )
        # 建议用独立变量名
    )

    agent = AssistantAgent(
        name="assistant",
        model_client=model_client,
        system_message="你是一个有用的助手。",
    )
    result = await agent.run(task="用一句话解释什么是 Agent。")
    for i, msg in enumerate(result.messages):
        print(f"--- 第 {i} 条 ---")
        print(f"类型: {type(msg).__name__}")
        print(f"来源: {msg.source}")
        print(f"内容: {msg.content}")

if __name__ == "__main__":
    asyncio.run(main())