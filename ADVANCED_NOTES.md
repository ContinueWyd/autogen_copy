# AutoGen 进阶学习笔记

> 目标：掌握 AutoGen 框架、消息协议、多 Agent 编排，并能做出"能给别人用"的项目。
> 方法：跑通 → 看消息流 → 对比差异 → 改 → 提交。

---

## 目录

- [一、总进度](#一总进度)
- [二、已学内容（全）](#二已学内容全)
- [三、环境信息](#三环境信息)
- [四、学习时间表](#四学习时间表)
- [五、关键代码模板](#五关键代码模板)
- [六、消息类型速查](#六消息类型速查)
- [七、编排方式对比](#七编排方式对比)
- [八、踩过的坑](#八踩过的坑)
- [九、学习资产](#九学习资产)
- [十、待办清单](#十待办清单)

---

## 一、总进度

### ✅ 已完成

- [x] 环境搭建（PyCharm + venv + AutoGen 0.4+）
- [x] 第三方模型接入（米醋API + DeepSeek）
- [x] 单 Agent
- [x] 工具调用（FunctionTool）
- [x] 多 Agent - RoundRobin
- [x] 多 Agent - Selector
- [x] 多 Agent - Swarm
- [x] 多 Agent - MagenticOne
- [x] CodeExecutorAgent
- [x] UserProxyAgent
- [x] 完整项目 A1（LeetCode Easy/Medium/Hard 全通过）
- [x] README_A1.md

### ⏳ 进行中

- [ ] 优先级 1：Agent 可靠性
- [ ] 优先级 2：Agent 记忆与状态
- [ ] 优先级 3：模型与成本
- [ ] 优先级 4：安全与边界
- [ ] 优先级 5：部署与工程化
- [ ] 优先级 6：高级编排
- [ ] 优先级 7：工具进阶
- [ ] 优先级 8：可观测性与调试

---

## 二、已学内容（全）

### 1. 环境与工具链

| 内容 | 说明 |
|---|---|
| AutoGen 0.4+ 安装 | `pip install autogen-agentchat autogen-ext[openai]` |
| 虚拟环境 | `.venv`，隔离依赖 |
| PyCharm 配置 | 解释器指向 `.venv`，Run Configuration 配环境变量 |
| GitHub Desktop | 克隆 fork、提交、推送、看历史 |
| 环境变量 | `DEEPSEEK_API_KEY`，用 `os.environ.get()` 读取 |
| 第三方模型接入 | 米醋API + `base_url` + `model_info` |

### 2. Agent 类型（3 种）

| Agent | 作用 | 关键参数 |
|---|---|---|
| AssistantAgent | 对话、推理、调用工具 | `model_client`、`system_message`、`tools`、`handoffs` |
| CodeExecutorAgent | 真正执行代码 | `code_executor`，不支持 handoffs |
| UserProxyAgent | 代表用户，可请求人工输入 | `input_func`，必须放进 Team |

### 3. 编排方式（4 种）

| 编排 | 谁决定下一个发言 | 需要额外模型 | 适合场景 |
|---|---|---|---|
| RoundRobinGroupChat | 框架固定轮流 | ❌ | 固定流程 |
| SelectorGroupChat | 模型选 | ✅ | 动态决策 |
| Swarm | 当前 Agent | ❌ | 条件流程、任务移交 |
| MagenticOneGroupChat | Orchestrator 规划 | ❌ | 复杂多步骤任务 |

### 4. 终止条件（2 种）

| 条件 | 作用 |
|---|---|
| MaxMessageTermination(n) | 最多 n 条消息就停 |
| TextMentionTermination("关键词") | 出现关键词就停 |

组合写法：`TextMentionTermination("TERMINATE") | MaxMessageTermination(10)`

### 5. 消息类型（8 种）

| 消息类型 | 出现时机 |
|---|---|
| TextMessage | 普通文本 |
| ThoughtEvent | 模型推理过程 |
| ToolCallRequestEvent | 模型决定调用工具 |
| ToolCallExecutionEvent | 工具执行完成 |
| ToolCallSummaryMessage | 工具结果汇总 |
| HandoffMessage | Swarm 里的任务移交 |
| UserInputRequestedEvent | UserProxyAgent 请求用户输入 |
| ModelClientStreamingChunkEvent | 流式输出（还没用过） |

### 6. 工具（FunctionTool）

```python
from autogen_core.tools import FunctionTool

def my_tool(arg: str) -> str:
    """工具描述，给模型看的。"""
    return "结果"

tool = FunctionTool(my_tool, description="工具说明")
```

### 7. 完整项目 A1

```
writer 写代码 → 调工具执行 → 交给 tester
tester 设计测试 → 调工具执行 → 交给 verifier
verifier 审查代码 → 通过 TERMINATE / 不通过交回 writer
```

- 编排方式：Swarm
- 执行器：包装成工具（绕开 CodeExecutorAgent 不支持 handoffs）
- 已验证：LeetCode Easy / Medium / Hard

---

## 三、环境信息

| 项目 | 内容 |
|---|---|
| 项目路径 | `D:\github-desktop-file\autogen_copy` |
| 虚拟环境 | `.venv` |
| Python 版本 | 3.11 |
| AutoGen 版本 | 0.4+（monorepo） |
| 模型平台 | 米醋API |
| 模型名 | deepseek-v4-flash |
| Base URL | `https://www.micuapi.ai/v1` |
| API Key 变量 | `DEEPSEEK_API_KEY` |

---

## 四、学习时间表

### 第 1 周：补齐"能跑 → 能用"的核心能力

| 天 | 学什么 | 具体内容 | 产出 |
|---|---|---|---|
| Day 1 | Agent 可靠性 | 重试机制、超时控制 | A1 加"工具失败自动重试" |
| Day 2 | Agent 可靠性 | 错误处理、fallback 模型 | A1 能优雅处理错误 |
| Day 3 | Agent 记忆 | 对话历史管理、State 保存 | A1 能"记住"上次任务 |
| Day 4 | Agent 记忆 | State 持久化、上下文压缩 | A1 能"今天问一半明天接着问" |
| Day 5 | 模型与成本 | token 统计、多模型混用 | A1 能统计成本、切换模型 |
| Day 6 | 模型与成本 | 成本控制、流式输出 | A1 有预算上限 |
| Day 7 | 休息 + 复盘 | 整理 NOTES.md | 完整学习档案 |

### 第 2 周：补上"真实项目必须"的能力

| 天 | 学什么 | 具体内容 | 产出 |
|---|---|---|---|
| Day 8 | 安全与边界 | Prompt Injection、代码隔离 | 了解风险 |
| Day 9 | 安全与边界 | 权限控制、输出过滤 | A1 加安全约束 |
| Day 10 | 部署与工程化 | Docker 执行器 | A1 换 Docker 执行 |
| Day 11 | 部署与工程化 | API 服务化 | A1 能通过 HTTP 调用 |
| Day 12 | 部署与工程化 | 并发处理、配置文件化 | A1 能处理多请求 |
| Day 13 | 高级编排 | 自定义终止条件 | 解决 A1 死循环的根因 |
| Day 14 | 高级编排 | 自定义 Selector、嵌套 Team | A1 编排更精细 |

### 第 3 周：锦上添花 + 做新项目

| 天 | 学什么 | 具体内容 | 产出 |
|---|---|---|---|
| Day 15 | 工具进阶 | 参数校验、并行调用 | A1 工具更稳 |
| Day 16 | 工具进阶 | MCP 协议、工具分组 | 接外部工具 |
| Day 17 | 可观测性 | 日志、Tracing | A1 能追踪调用链 |
| Day 18 | 可观测性 | AutoGen Studio、评测 | 可视化 + 测试 |
| Day 19-21 | 做 A2 或 A3 | 用学到的全部知识做新项目 | 第二个完整项目 |

---

## 五、关键代码模板

### 5.1 模型客户端

```python
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo

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
```

### 5.2 工具定义

```python
from autogen_core.tools import FunctionTool

def get_weather(city: str) -> str:
    """查询指定城市的天气。"""
    return f"{city}：晴天，25°C"

weather_tool = FunctionTool(get_weather, description="查询城市天气")
```

### 5.3 单 Agent

```python
from autogen_agentchat.agents import AssistantAgent

agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    system_message="你是一个有用的助手。",
)
result = await agent.run(task="...")
```

### 5.4 多 Agent（RoundRobin）

```python
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination

termination = TextMentionTermination("TERMINATE") | MaxMessageTermination(10)

team = RoundRobinGroupChat(
    participants=[writer, reviewer],
    termination_condition=termination,
)
result = await team.run(task="...")
```

### 5.5 多 Agent（Selector）

```python
from autogen_agentchat.teams import SelectorGroupChat

team = SelectorGroupChat(
    participants=[writer, reviewer],
    model_client=model_client,
    termination_condition=TextMentionTermination("TERMINATE"),
)
```

### 5.6 多 Agent（Swarm）

```python
from autogen_agentchat.teams import Swarm

writer = AssistantAgent(
    name="writer",
    model_client=model_client,
    handoffs=["executor"],
)
team = Swarm(
    participants=[writer, executor],
    termination_condition=TextMentionTermination("TERMINATE"),
)
```

### 5.7 代码执行器（包装成工具）

```python
from autogen_core.tools import FunctionTool
from autogen_core import CancellationToken, CodeBlock
from autogen_ext.code_executors.local import LocalCommandLineCodeExecutor

code_executor = LocalCommandLineCodeExecutor(work_dir="code_exec_tmp", timeout=10)

async def execute_python_code(code: str) -> str:
    result = await code_executor.execute_code_blocks(
        code_blocks=[CodeBlock(code=code, language="python")],
        cancellation_token=CancellationToken(),
    )
    return result.output

execute_tool = FunctionTool(execute_python_code, description="执行 Python 代码")
```

---

## 六、消息类型速查

| 消息类型 | 出现时机 | 来源 |
|---|---|---|
| TextMessage | 普通文本 | user / 各 Agent |
| ThoughtEvent | 模型推理 | 各 Agent |
| ToolCallRequestEvent | 决定调工具 | 调用者 |
| ToolCallExecutionEvent | 工具执行完 | 调用者 |
| ToolCallSummaryMessage | 工具结果汇总 | 调用者 |
| HandoffMessage | Swarm 移交 | 移交者 |
| UserInputRequestedEvent | 请求用户输入 | UserProxyAgent |

---

## 七、编排方式对比

### RoundRobinGroupChat

| 维度 | 说明 |
|---|---|
| 谁决定下一个发言 | 框架固定轮流 |
| 必须参数 | `participants` |
| Agent 需要 description | 不需要 |
| 可预测性 | 高 |
| 适合 | 固定流程 |

### SelectorGroupChat

| 维度 | 说明 |
|---|---|
| 谁决定下一个发言 | 模型选 |
| 必须参数 | `participants` + `model_client` |
| Agent 需要 description | 需要 |
| 可预测性 | 低 |
| 适合 | 动态决策 |

### Swarm

| 维度 | 说明 |
|---|---|
| 谁决定下一个发言 | 当前 Agent |
| 必须参数 | `participants` + `handoffs` |
| 移交机制 | 工具调用 |
| 独有消息 | HandoffMessage |
| 适合 | 条件流程、任务移交 |

### MagenticOneGroupChat

| 维度 | 说明 |
|---|---|
| 谁决定下一个发言 | Orchestrator |
| 特点 | 先规划、再派活、后汇总 |
| 适合 | 复杂多步骤任务 |

---

## 八、踩过的坑

| 坑 | 原因 | 修法 |
|---|---|---|
| model_info is required | 非 OpenAI 模型不在白名单 | 手动配 model_info |
| Missing credentials | 环境变量没读到 | 配 Run Configuration 或系统变量 |
| Authentication Fails | key 和 base_url 不匹配 | 必须来自同一平台 |
| 'tuple' object has no attribute 'language' | execute_code_blocks 参数错 | 用 CodeBlock 对象 |
| missing cancellation_token | 参数缺失 | 加 CancellationToken() |
| CodeExecutorAgent 不支持 handoffs | 它不调用模型 | 包装成工具 |
| verifier 说完不通过就停 | RoundRobin 不适合条件流程 | 改用 Swarm |
| 死循环 47 条 | verifier 通过但没 TERMINATE | system_message 明确"只说 TERMINATE" |
| TextMentionTermination 提前终止 | 关键词撞车 | 用专属关键词 |
| GitHub push 失败 | 网络问题 | 配代理或重试 |

---

## 九、学习资产

| 资产 | 位置 | 状态 |
|---|---|---|
| 单 Agent | `run_autogen.py` | ✅ |
| 多 Agent（RoundRobin） | `run_multi_agent.py` | ✅ |
| 多 Agent（Selector） | `run_selector.py` | ✅ |
| 多 Agent（Swarm） | `run_swarm.py` | ✅ |
| 多 Agent（MagenticOne） | `run_magentic.py` | ✅ |
| CodeExecutorAgent | `run_code_exec.py` | ✅ |
| UserProxyAgent | `run_user_proxy.py` | ✅ |
| 完整项目 A1 | `run_code_assistant.py` | ✅ |
| A1 文档 | `README_A1.md` | ✅ |
| 学习笔记 | `NOTES.md` | ✅ 本文件 |

---

## 十、待办清单

### 优先级 1：Agent 可靠性（Day 1-2）
- [ ] 工具调用失败自动重试
- [ ] 超时控制
- [ ] 错误处理
- [ ] fallback 模型
- [ ] 人工审批（approval_func）

### 优先级 2：Agent 记忆与状态（Day 3-4）
- [ ] 对话历史管理
- [ ] State 持久化
- [ ] 上下文压缩

### 优先级 3：模型与成本（Day 5-6）
- [ ] token 统计
- [ ] 多模型混用
- [ ] 成本控制
- [ ] 流式输出

### 优先级 4：安全与边界（Day 8-9）
- [ ] Prompt Injection 防护
- [ ] 代码执行隔离
- [ ] 权限控制
- [ ] 输出过滤

### 优先级 5：部署与工程化（Day 10-12）
- [ ] Docker 执行器
- [ ] API 服务化
- [ ] 并发处理
- [ ] 配置文件化

### 优先级 6：高级编排（Day 13-14）
- [ ] 自定义终止条件
- [ ] 自定义 Selector
- [ ] 嵌套 Team
- [ ] 图编排（GraphFlow）

### 优先级 7：工具进阶（Day 15-16）
- [ ] 工具参数校验
- [ ] 工具并行调用
- [ ] 工具结果缓存
- [ ] MCP 协议
- [ ] 工具分组

### 优先级 8：可观测性与调试（Day 17-18）
- [ ] 日志
- [ ] 追踪（Tracing）
- [ ] AutoGen Studio
- [ ] 评测

### 最终目标：做 A2 或 A3（Day 19-21）
- [ ] 选一个项目
- [ ] 用学到的全部知识做
- [ ] 独立成项目 + README