# AutoGen 学习笔记

> 目标：掌握 AutoGen 框架、消息协议、多 Agent 编排方式。
> 方法：跑通 → 看消息流 → 对比差异 → 改 → 提交。

---

## 目录

- [一、当前进度](#一当前进度)
- [二、环境信息](#二环境信息)
- [三、项目文件结构](#三项目文件结构)
- [四、关键代码模板](#四关键代码模板)
- [五、消息类型速查](#五消息类型速查)
- [六、编排方式对比](#六编排方式对比)
- [七、关键结论](#七关键结论)
- [八、下一步计划](#八下一步计划)
- [九、学习资产](#九学习资产)
- [十、待解决问题](#十待解决问题)

---

## 一、当前进度

### ✅ 已完成

- [x] 环境搭建（PyCharm + venv + AutoGen 源码）
- [x] 配置第三方模型（米醋API + DeepSeek）
- [x] 单 Agent 最小对话
- [x] 工具调用（FunctionTool）
- [x] 多 Agent 协作（RoundRobinGroupChat）
- [x] 终止条件（MaxMessageTermination / TextMentionTermination）
- [x] SelectorGroupChat（选择器决定下一个谁发言）

### ⏳ 进行中

- [ ] 掌握多种编排方式（Swarm / MagenticOneGroupChat 待学）
- [ ] 完整项目（把学到的串起来）

### ❌ 已明确不学

- [ ] 读 AutoGen 源码（目标是"用好"，不是"造框架"）
- [ ] 给框架做贡献

---

## 二、环境信息

| 项目 | 内容 |
|---|---|
| 项目路径 | `D:\github-desktop-file\autogen_copy` |
| 虚拟环境 | `.venv` |
| Python 版本 | 3.11 |
| AutoGen 版本 | 0.4+（monorepo） |
| 模型平台 | 米醋API（第三方中转站） |
| 模型名 | deepseek-v4-flash |
| Base URL | `https://www.micuapi.ai/v1` |
| API Key 变量 | `DEEPSEEK_API_KEY` |

---

## 三、项目文件结构

```
autogen_copy/
├── run_autogen.py          ← 单 Agent（已跑通）
├── run_multi_agent.py      ← 多 Agent（RoundRobin）
├── run_selector.py         ← 多 Agent（Selector）
├── NOTES.md                ← 本文件
├── .venv/                  ← 虚拟环境
└── python/                 ← AutoGen 源码（不读，只查）
```

---

## 四、关键代码模板

### 4.1 模型客户端

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

### 4.2 工具定义

```python
from autogen_core.tools import FunctionTool

def get_weather(city: str) -> str:
    """查询指定城市的天气。

    Args:
        city: 城市名称。
    """
    return f"{city}：晴天，25°C"

weather_tool = FunctionTool(get_weather, description="查询城市天气")
```

### 4.3 单 Agent

```python
from autogen_agentchat.agents import AssistantAgent

agent = AssistantAgent(
    name="assistant",
    model_client=model_client,
    system_message="你是一个有用的助手。",
)
result = await agent.run(task="...")
```

### 4.4 多 Agent（RoundRobin 轮流发言）

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

### 4.5 多 Agent（Selector 选择器决定发言人）

```python
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.conditions import TextMentionTermination

team = SelectorGroupChat(
    participants=[writer, reviewer],
    model_client=model_client,       # 必须传，选择器用它来决定谁发言
    termination_condition=TextMentionTermination("TERMINATE"),
)
result = await team.run(task="...")
```

---

## 五、消息类型速查

| 消息类型 | 出现时机 | 来源 |
|---|---|---|
| `TextMessage` | 普通文本，用户输入或模型回复 | user / 各 Agent |
| `ThoughtEvent` | 模型的推理过程（不一定每次都有） | 各 Agent |
| `ToolCallRequestEvent` | 模型决定调用工具 | 调用工具的 Agent |
| `ToolCallExecutionEvent` | 工具执行完成，返回结果 | 调用工具的 Agent |
| `ToolCallSummaryMessage` | 工具结果被汇总成最终消息 | 调用工具的 Agent |

**规律**：

- 有工具调用 → 消息流变长（多出 3 条）
- 有多个 Agent → `source` 字段变多
- 任务简单 → 没有 `ThoughtEvent`

---

## 六、编排方式对比

### RoundRobinGroupChat

| 维度 | 说明 |
|---|---|
| 谁决定下一个发言 | 框架固定轮流 |
| 必须参数 | `participants` |
| Agent 需要 `description` 吗 | 不需要 |
| 行为可预测性 | **高** |
| 适合场景 | 流程固定、需要确定性（写→审→改） |

### SelectorGroupChat

| 维度 | 说明 |
|---|---|
| 谁决定下一个发言 | **模型根据对话内容决定** |
| 必须参数 | `participants` + **`model_client`** |
| Agent 需要 `description` 吗 | **需要**，模型靠它判断 |
| 行为可预测性 | **低** |
| 适合场景 | 任务需要动态决策、角色不固定 |

---

## 七、关键结论

1. **`model_info` 必须手动配**：非 OpenAI 官方模型不在白名单里，必须告诉 AutoGen 该模型的能力（特别是 `function_calling`）。
2. **环境变量按运行配置隔离**：PyCharm 每个脚本有独立 Run Configuration，新脚本要重新配环境变量，或用模板统一配置。
3. **`FunctionTool` 的 docstring 是给模型看的**：写得越清楚，模型调用越准。
4. **AutoGen 默认不在工具调用后重新问模型**：工具结果直接作为最终消息返回（`ToolCallSummaryMessage`），不再多调一次模型。
5. **`TextMentionTermination` 是省钱的关键**：只用 `MaxMessageTermination` 会跑满上限；加上 `TERMINATE` 检测，Agent 一说就停。
6. **终止条件组合用 `|` 不能用 `,`**：`|` 是或条件对象，`,` 会变成元组导致报错。
7. **SelectorGroupChat 的行为有随机性**：同样的 task 和配置，每次运行可能不同。
   - 第 1 次：writer 写了两个版本，reviewer 发现 `fib_fast` 缺负数校验 → 不通过
   - 第 2 次：writer 只写了一个版本，reviewer 通过并输出 TERMINATE
   - 原因：选择器由模型决定，模型输出有随机性
8. **Selector 可能"选不出人"提前停**：当选择器判断"没人该说话了"，任务会结束，不会等到 `TERMINATE`。
9. **第三方平台可能临时连不上**：报 `APIConnectionError` / `httpx2.ConnectError` 时，不是代码问题，重试或等一会儿。
10. **Swarm 的移交本质是工具调用**：`handoffs=["coder"]` 会自动生成一个 `transfer_to_coder` 工具，Agent 调用它即完成移交。
11. **`HandoffMessage` 是 Swarm 独有的消息类型**：标志任务从一个 Agent 移交给另一个。
12. **Swarm 不需要选择器模型**：和 Selector 不同，Swarm 靠 Agent 自己"说"要交给谁。
13. **Swarm 的参与者顺序有讲究**：`participants` 列表里第一个 Agent 总是先发言，通常放"分流员"。
14. **Selector 需要额外模型，RoundRobin 和 Swarm 不需要**：
    - RoundRobin：下一个谁发言，框架写死，不需要问模型
    - Selector：需要额外调一次模型，让它选下一个发言者（这就是它的 `model_client` 参数的用途）
    - Swarm：当前 Agent 发言时顺便说"交给谁"，不需要额外问

15. **Agent 数量由你决定，不由编排方式决定**：
    - 三种编排都可以用任意数量的 Agent
    - 我之前用 Swarm 放 3 个 Agent，是因为要演示"分流 + 两个专家"的场景
    - RoundRobin 和 Selector 放 2 个，是因为"写 + 审"两个角色就够
    - 原则：每个 Agent 都要有明确、不重复的角色
16. **Selector 的额外模型开销是机制性的**：
    - `SelectorGroupChat` 必须传 `model_client`
    - 每轮发言前会额外调一次模型，让它决定"下一个谁发言"
    - 同样 4 轮对话，Selector 的模型调用次数约是 RoundRobin 的 2 倍
    - 这是 Selector 独有的成本

17. **Swarm 不需要额外模型，也不强制要求分流 Agent**：
    - 移交是当前 Agent"顺便"做的，不额外调用模型
    - 你可以放一个 triage 分流员，但那是设计选择，不是框架要求
    - Swarm 的 participants 放任意数量和角色都可以
18. **MagenticOneOrchestrator 是 MagenticOne 独有的角色**：
    - 它相当于"项目经理"，负责规划、派活、跟踪、汇总
    - 其他三种编排（RoundRobin/Selector/Swarm）都没有这个角色

19. **MagenticOne 的工作流是"先规划，再执行"**：
    - 第一步：制定"任务台账"（团队、事实、待查项、计划）
    - 第二步：把子任务派给合适的 Agent
    - 第三步：汇总结果
    - 复杂任务还会有第四步：进度跟踪、重新规划

20. **MagenticOne 适合复杂、多步骤、开放的任务**：
    - 简单任务（解释一个词）用它是"杀鸡用牛刀"
    - 它的价值在"任务需要多次迭代才能完成"时才会体现
    - 学习阶段知道它"是什么、解决什么问题"就够了，不必深入
---

## 八、下一步计划

### 阶段1：补全编排方式（进行中）

- [x] `RoundRobinGroupChat`
- [x] `SelectorGroupChat`
- [ ] `Swarm`
- [ ] `MagenticOneGroupChat`（如果版本支持）

### 阶段2：扩展 Agent 类型（可选）

- [ ] `CodeExecutorAgent`（能执行代码）
- [ ] `UserProxyAgent`（人工介入）

### 阶段3：完整项目

- [ ] 选题：多 Agent 研究助手 / 代码生成器 / 数据分析
- [ ] 设计：角色、工具、编排、终止条件
- [ ] 实现、跑通、提交

---

## 九、学习资产

| 资产 | 位置 | 状态 |
|---|---|---|
| 单 Agent 代码 | `run_autogen.py` | ✅ 可跑 |
| 多 Agent 代码（RoundRobin） | `run_multi_agent.py` | ✅ 可跑 |
| 多 Agent 代码（Selector） | `run_selector.py` | ✅ 可跑 |
| AutoGen 源码 | `python/packages/` | ✅ 已克隆（仅查询） |
| 学习笔记 | `NOTES.md` | ✅ 本文件 |

---

## 十、待解决问题

- [ ] GitHub 推送网络问题（`The remote disconnected`）——偶发，重试即可
- [ ] `Swarm` 和 `MagenticOneGroupChat` 的用法和适用场景
- [ ] 如何让 Selector 在"审查不通过"后自动让 writer 修改

---

## 附录：常用命令

```bash
# 激活虚拟环境（Windows PowerShell）
.venv\Scripts\activate

# 运行脚本
python run_autogen.py
python run_multi_agent.py
python run_selector.py

# 验证环境变量
echo $env:DEEPSEEK_API_KEY
```