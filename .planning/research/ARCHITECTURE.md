# Architecture Research

**Domain:** Agent Skill for IoT Device Data API
**Researched:** 2026-05-13
**Confidence:** HIGH

## Standard Architecture

### Skill.md Structure Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      YAML Frontmatter                        │
│  (name, description, version, author, platform hints)       │
├─────────────────────────────────────────────────────────────┤
│                      Skill Identity                          │
│  (What this skill does, who it''s for, core value)          │
├─────────────────────────────────────────────────────────────┤
│                      API Context                             │
│  (Base URL, auth method, rate limits, error codes)          │
├─────────────────────────────────────────────────────────────┤
│                      Available Tools                         │
│  (Function schemas: name, description, parameters)          │
├─────────────────────────────────────────────────────────────┤
│                      Interaction Patterns                    │
│  (How users should ask, how skill responds)                 │
├─────────────────────────────────────────────────────────────┤
│                      Conversation Examples                   │
│  (User message → Skill thought → Tool call → Response)      │
├─────────────────────────────────────────────────────────────┤
│                      Output Formats                          │
│  (Tables, summaries, reports, how to present data)          │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| YAML Frontmatter | 平台元数据、技能注册信息 | YAML 键值对 |
| Skill Identity | 告诉 Agent"我是谁、我能做什么" | 2-3 句描述 + 能力清单 |
| API Context | 提供调用 API 所需的全部上下文 | Base URL + Auth 说明 + 环境配置 |
| Available Tools | 结构化描述每个可调用的 API | JSON Schema 格式的 function 定义 |
| Interaction Patterns | 定义用户如何与 skill 交互 | 示例对话 + 指令模板 |
| Conversation Examples | 少样本学习，展示正确行为 | 3-5 组完整对话示例 |
| Output Formats | 规范数据呈现方式 | Markdown 表格模板 + 格式化指令 |

## Recommended Project Structure

```
insentek-api-skills/
├── skill.md                    # 主技能文件（交付核心）
├── docs/
│   ├── getting-started.md      # 快速上手指南
│   ├── platform-setup.md       # 各平台配置说明
│   └── api-reference.md        # API 参数详细说明
├── examples/
│   ├── queries.md              # 查询类对话示例
│   ├── reports.md              # 报告生成示例
│   └── alerts.md               # 实时分析示例
└── .planning/                  # GSD 规划文件
```

### Structure Rationale

- **skill.md:** 单文件交付物，包含所有核心能力定义
- **docs/:** 降低用户上手门槛，覆盖常见使用场景
- **examples/:** 具体可复制的对话示例，比抽象说明更有效

## Architectural Patterns

### Pattern 1: Function-First Skill Design

**What:** 优先定义 function schema，用结构化方式描述 API 能力
**When to use:** Agent 平台支持 function calling 时（Claude、ChatGPT 等）
**Trade-offs:**
- Pros: Agent 调用精确，参数类型安全，可验证
- Cons: 部分平台不支持，需要维护 schema

**Example:**
```yaml
tools:
  - name: query_device_data
    description: 查询指定设备的数据
    parameters:
      type: object
      properties:
        device_id:
          type: string
          description: 设备唯一标识
        start_time:
          type: string
          description: 查询开始时间（ISO 8601）
```

### Pattern 2: Prompt-First Skill Design

**What:** 用自然语言描述所有能力和使用方式
**When to use:** 平台不支持 function calling，或需要最大兼容性
**Trade-offs:**
- Pros: 跨平台兼容，无需维护 schema，表达灵活
- Cons: Agent 理解可能不一致，参数构造可能出错

### Pattern 3: Hybrid Design (Recommended)

**What:** Function schema 定义精确能力 + Prompt 补充上下文和示例
**When to use:** 追求精确性和兼容性的平衡
**Trade-offs:**
- Pros: 精确调用 + 灵活理解，适配多平台
- Cons: 文件较长，需要维护两部分内容

## Data Flow

### User → Skill → API → Response Flow

```
User Query (自然语言)
    ↓
Skill Intent Recognition (解析用户意图)
    ↓
Parameter Extraction (提取 API 参数)
    ↓
API Request Construction (构造 HTTP 请求)
    ↓
insentek API Response (JSON 数据)
    ↓
Data Transformation (转换为可读格式)
    ↓
User-Facing Response (Markdown 表格/总结)
```

## Anti-Patterns

### Anti-Pattern 1: 隐式假设

**What people do:** 假设用户知道设备 ID、API 密钥位置等
**Why it''s wrong:** 终端用户是非技术人员，不知道这些技术细节
**Do this instead:** 明确引导用户获取必要信息，提供 step-by-step 指引

### Anti-Pattern 2: 裸数据转储

**What people do:** 直接输出原始 JSON 给用户
**Why it''s wrong:** 用户无法阅读原始数据，体验极差
**Do this instead:** 总是将数据转换为表格、总结或可视化描述

---
*Architecture research for: Agent Skill for IoT Device Data API*
*Researched: 2026-05-13*
