# Platform Setup Guide — 各 Agent 平台配置指南

> 将 insentek skill 安装到不同 Agent 平台的完整步骤，含安装路径、卸载方法和故障排查。

---

## 目录

- [OpenClaw](#openclaw)
- [Claude Code](#claude-code)
- [ChatGPT](#chatgpt)
- [Hermes-Agent](#hermes-agent)
- [平台兼容性速查](#平台兼容性速查)
- [故障排查](#故障排查)

---

## OpenClaw

### 安装

#### 方式一：从 ClawHub 安装（推荐）

```bash
# 安装最新版本
clawhub skill install insentek-api-skill

# 安装指定版本
clawhub skill install insentek-api-skill@1.0.3

# 从 ClawHub 搜索确认
clawhub skill search insentek
```

安装完成后，skill 会自动注册到 OpenClaw 的技能列表中。

#### 方式二：本地文件安装

```bash
# 从本地 skill.md 安装
clawhub skill add ./skill.md

# 或使用绝对路径
clawhub skill add /path/to/skill.md
```

#### 方式三：Web UI 安装

1. 打开 OpenClaw 客户端，进入 **Skills** 页面
2. 点击 **Import Skill** → 选择文件
3. 选择项目根目录的 `skill.md` 文件
4. 确认导入

### 卸载

```bash
# CLI 卸载
clawhub skill remove insentek-api-skill
```

或在 Web UI 中：Skills → 找到 "insentek-api-skill" → **Remove**。

### 配置参数

| 参数 | 值 | 说明 |
|------|-----|------|
| API Base URL | `http://openapi.ecois.info` | 默认即可 |

### 首次使用

```
User: 我的 appid 是 xxx，secret 是 yyy，查看所有设备
```

OpenClaw 会自动解析 skill.md 中的 function schema 并调用 authenticate 工具。

---

## Claude Code

### 安装

Claude Code 通过读取 skill 文件来加载技能上下文，支持项目级和全局级两种方式。

#### 方式一：全局 Skills 目录（推荐）

Claude Code 会从全局 skills 目录自动加载所有 skill 文件，无需在每个项目中重复放置。

**Windows:**
```powershell
# 创建 skills 目录（如果不存在）
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.claude\skills"

# 复制 skill 文件
Copy-Item skill.md "$env:USERPROFILE\.claude\skills\insentek-api-skill.md"
```

**macOS:**
```bash
mkdir -p ~/.claude/skills
cp skill.md ~/.claude/skills/insentek-api-skill.md
```

**Linux:**
```bash
mkdir -p ~/.claude/skills
cp skill.md ~/.claude/skills/insentek-api-skill.md
```

放置后重启 Claude Code 或重新打开对话即可生效。

#### 方式二：项目目录加载

将 `skill.md` 放入当前工作项目的根目录，Claude Code 会自动识别为项目上下文：

```bash
# 任意项目目录
cp skill.md ./skill.md
```

#### 方式三：对话中直接引用

```
# 在 Claude Code 对话中执行
/load skill.md
```

或直接将 `skill.md` 内容粘贴到对话中。

### 卸载

- **全局级（推荐）**：从 `~/.claude/skills/` 目录移除对应文件
  ```bash
  # Windows
  Remove-Item "$env:USERPROFILE\.claude\skills\insentek-api-skill.md"

  # macOS / Linux
  rm ~/.claude/skills/insentek-api-skill.md
  ```
- **项目级**：删除项目根目录的 `skill.md` 文件
- **对话级**：执行 `/clear` 清除当前对话上下文

### 首次使用

```
User: 我的 appid 是 xxx，secret 是 yyy，查看所有设备
```

Claude Code 会读取 skill.md 中的 tool definitions，使用 function calling 调用 API。

### 注意事项

- 确保 skill.md 中的 YAML frontmatter 被正确解析
- 如果 function calling 未触发，尝试明确说出工具名称如 "query_device"

---

## ChatGPT

### 安装

#### 方式一：创建 GPT（推荐，需 Plus 订阅）

1. 打开 [ChatGPT](https://chat.openai.com) → **Explore GPTs** → **Create**
2. 在 Configure 标签页：
   - **Name**: Insentek Device Query
   - **Description**: 查询 insentek 物联网设备数据
   - **Instructions**: 粘贴 `skill.md` 的完整内容
3. 在 **Capabilities** 中启用 "Code Interpreter"（如需数据处理）
4. 保存并发布（可选设为 Private）

#### 方式二：Actions（API 直连，需 Plus 订阅）

1. 创建 GPT 时，在 Configure 页面点击 **Add actions**
2. 粘贴由 `skill.md` function schema 生成的 OpenAPI schema
3. 设置认证方式：API Key（Header: `Authorization`）
4. 保存后 GPT 可直接调用 insentek API

#### 方式三：Custom Instructions（个人使用）

适合临时使用，无需创建 GPT。

1. 打开 ChatGPT → 点击头像 → **Custom Instructions**
2. 在 "How would you like ChatGPT to respond?" 中粘贴 `skill.md` 的 Prompt 区内容
3. 在 "What would you like ChatGPT to know about you?" 中填入：
   ```
   我有 insentek 物联网设备，appid: xxx, secret: yyy
   ```
4. 保存后开始新对话

**限制：** Custom Instructions 不支持真正的 function calling，API 调用需要手动复制 URL。

### 卸载

- **GPTs 方式**：ChatGPT → Explore GPTs → 找到对应 GPT → 右上角 ⋮ → **Delete GPT**
- **Actions 方式**：编辑 GPT → Configure → Actions → **删除对应 Action**
- **Custom Instructions**：ChatGPT → 头像 → Custom Instructions → **清空内容**

### 首次使用

```
User: 查看我的所有设备
```

如果已配置 appid/secret，ChatGPT 会自动认证并查询。

---

## Hermes-Agent

### 安装

Hermes-Agent 通过读取 skills 目录下的 skill 文件来加载技能。

#### 步骤

**Windows:**
```powershell
# 创建 skills 目录（如果不存在）
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.hermes\skills"

# 复制 skill 文件
Copy-Item skill.md "$env:USERPROFILE\.hermes\skills\insentek-api-skill.md"
```

**macOS:**
```bash
mkdir -p ~/.hermes/skills
cp skill.md ~/.hermes/skills/insentek-api-skill.md
```

**Linux:**
```bash
mkdir -p ~/.hermes/skills
cp skill.md ~/.hermes/skills/insentek-api-skill.md
```

**重启或刷新：**
```bash
hermes skill reload
# 或重启 Hermes-Agent 服务
```

### 卸载

**Windows:**
```powershell
Remove-Item "$env:USERPROFILE\.hermes\skills\insentek-api-skill.md"
```

**macOS / Linux:**
```bash
rm ~/.hermes/skills/insentek-api-skill.md
hermes skill reload
```

### 配置环境变量（可选）

```bash
export INSENTEK_BASE_URL=http://openapi.ecois.info
```

### 首次使用

```
User: appid xxx secret yyy，查看设备
```

Hermes-Agent 会解析 skill.md 中的工具定义并执行对应动作。

---

## 平台兼容性速查

| 特性 | OpenClaw | Claude Code | ChatGPT (GPTs) | Hermes-Agent |
|------|----------|-------------|----------------|--------------|
| Function Schema | Native | Native | Via Actions | Native |
| YAML Frontmatter | ✅ | ✅ | ⚠️ | ✅ |
| Auto Token Refresh | ✅ | ✅ | Manual | ✅ |
| Alias Resolution | ✅ | ✅ | ✅ | ✅ |
| Time Parsing | ✅ | ✅ | ✅ | ✅ |
| Chain Calling | ✅ | ✅ | ✅ | ✅ |
| ClawHub 一键安装 | ✅ | ❌ | ❌ | ❌ |

**图例：** ✅ 原生支持 | ⚠️ 需额外配置 | ❌ 不支持

---

## 故障排查

### Function Schema 未被识别

- **Claude Code**: 确保 skill.md 位于项目根目录，且文件名为 `skill.md`
- **ChatGPT**: 使用 GPTs 的 Actions 功能，或手动粘贴 Instructions
- **通用**: 检查 YAML frontmatter 格式是否正确（`---` 开头和结尾）

### 认证失败

1. 确认 appid 和 secret 正确（无多余空格）
2. 检查网络是否能访问 `http://openapi.ecois.info`
3. 确认 token 未过期（skill 会自动刷新，但首次需手动提供）

### 查询无数据返回

1. 确认设备已正确接入 insentek 平台
2. 检查时间范围是否合理（默认最近 24 小时可能无数据）
3. 尝试扩大时间范围如 "最近7天"

---

*配置问题请联系：参考 insentek 官方支持渠道*
