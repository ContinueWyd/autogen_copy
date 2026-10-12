import asyncio
import os
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.tools import FunctionTool
from autogen_core.models import ModelInfo


# 1. 定义工具函数
def get_weather(city: str) -> str:
    """查询指定城市的天气。

    Args:
        city: 城市名称，比如"北京"、"上海"。
    """
    # 这里用假数据，重点看 Agent 会不会调用它
    fake_data = {
        "北京": "晴天，25°C，湿度 40%",
        "上海": "多云，22°C，湿度 65%",
        "广州": "小雨，28°C，湿度 80%",
    }
    return fake_data.get(city, f"{city}：暂无数据")


async def main():
    # 2. 配置模型客户端
    model_client = OpenAIChatCompletionClient(
        model="deepseek-v4-flash",
        base_url="https://www.micuapi.ai/v1",
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        model_info=ModelInfo(
            vision=False,
            function_calling=True,   # 必须 True，否则工具调用不生效
            json_output=True,
            structured_output=False,
            family="unknown",
        ),
    )

    # 3. 把普通函数包装成 AutoGen 能识别的工具
    weather_tool = FunctionTool(
        get_weather,
        description="查询指定城市的天气",
    )

    # 4. 创建 Agent，把工具传进去
    agent = AssistantAgent(
        name="assistant",
        model_client=model_client,
        tools=[weather_tool],
        system_message="你是一个有用的助手，可以查询天气。",
    )

    # 5. 跑一个会触发工具调用的任务
    result = await agent.run(task="北京今天天气怎么样？")

    # 6. 打印全部消息，观察工具调用过程
    for i, msg in enumerate(result.messages):
        print(f"--- 第 {i} 条 ---")
        print(f"类型: {type(msg).__name__}")
        print(f"来源: {msg.source}")
        print(f"内容: {msg.content}")
        print()


if __name__ == "__main__":
    asyncio.run(main())