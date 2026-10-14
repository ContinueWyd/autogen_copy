# A1: 多 Agent 代码助手

基于 AutoGen 0.4+ 的多 Agent 系统，能自动"写代码 → 执行 → 测试 → 验证"。

## 架构

- **writer**：写代码，调工具执行
- **tester**：设计测试用例，验证功能
- **verifier**：独立审查代码，最终确认

编排方式：`Swarm`（Agent 自己决定移交给谁）

## 工作流

```
writer 写代码 → 调工具执行 → 交给 tester
tester 设计测试 → 调工具执行 → 交给 verifier
verifier 审查代码 → 通过 TERMINATE / 不通过交回 writer
```

## 依赖

- Python 3.10+
- AutoGen 0.4+（`autogen-agentchat`、`autogen-ext`）
- 一个 OpenAI 兼容的模型 API

## 运行

```bash
# 激活虚拟环境
.venv\Scripts\activate

# 设置 API Key（Windows PowerShell）
$env:DEEPSEEK_API_KEY="sk-..."

# 运行
python run_code_assistant.py
```

## 已验证

- LeetCode Easy（两数之和）：✅
- LeetCode Medium（最长回文子串）：✅
- LeetCode Hard（正则表达式匹配）：✅

## 已知限制

- 执行器在本地跑，有安全风险（生产环境应换 Docker）
- verifier 读代码依赖 writer/tester 主动贴代码
- 终止机制依赖 TERMINATE 关键词