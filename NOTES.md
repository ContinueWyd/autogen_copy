# AutoGen 学习笔记

## 已完成
- 单 Agent
- 工具调用
- RoundRobinGroupChat 双 Agent
- TextMentionTermination 终止条件

## 消息类型速查
- TextMessage：普通文本
- ThoughtEvent：模型思考
- ToolCallRequestEvent：请求调工具
- ToolCallExecutionEvent：工具执行结果
- ToolCallSummaryMessage：工具结果汇总

## 待学
- SelectorGroupChat
- Swarm
- 消息协议全貌





阶段1：补全框架认知（2-3天）
目标：知道 AutoGen 有哪些积木。

要看的：

autogen_agentchat/agents/ 下有哪些 Agent 类型

autogen_agentchat/teams/ 下有哪些 Team 类型

产出：一张"积木清单"。

阶段2：吃透消息协议（3-4天）
目标：从消息流反推 Agent 在做什么。

要看的：

autogen_agentchat/messages.py 里的 ChatMessage 体系

每个消息类型的定义和用途

产出：一张"消息类型全表"。

阶段3：掌握多种编排（5-7天）
目标：能根据任务选对 Team。

要学的：

RoundRobinGroupChat ✅ 已会

SelectorGroupChat（选择器决定下一个谁发言）

Swarm（Agent 之间移交任务）

MagenticOneGroupChat（如果版本支持）

产出：每种 Team 一个最小示例 + 消息流对比。

阶段4：做一个完整项目（7-10天）
目标：把学到的串起来。

建议项目：多 Agent 研究助手 / 代码生成器 / 数据分析。

产出：一个能跑、能解释、能提交到 GitHub 的项目。