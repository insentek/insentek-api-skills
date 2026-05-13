# Platform Setup Guide — 各 Agent 平台配置指南

> 将 insentek skill 加载到不同 Agent 平台的具体步骤。

---

## 目录

- [OpenClaw](#openclaw)
- [Claude Code](#claude-code)
- [ChatGPT](#chatgpt)
- [Hermes-Agent](#hermes-agent)

---

## OpenClaw

### 步骤

1. 打开 OpenClaw 客户端，进入 **Skills** 页面
2. 点击 **Import Skill** → 选择文件
3. 选择项目根目录的 `skill.md` 文件
4. 确认导入后，在对话中直接开始使用

### 配置参数

导入时可能需要填写：

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

### 方法一：项目目录加载（推荐）

1. 将 `skill.md` 放入你的工作项目目录
2. 在 Claude Code 中打开该目录
3. Claude Code 会自动识别 skill.md 作为项目上下文

```bash
# 示例目录结构
my-project/
├── skill.md          # 放入此文件
├── src/
└── ...
```

### 方法二：直接粘贴

1. 打开 Claude Code 对话
2. 将 `skill.md` 的完整内容粘贴到对话中
3. 告诉 Claude："请根据这份 skill 文件帮我查询 insentek 设备数据"

### 首次使用

```
User: 我的 appid 是 xxx，secret 是 yyy，查看所有设备
```

Claude Code 会读取 skill.md 中的 tool definitions，使用 function calling 调用 API。

### 注意事项

- Claude Code 支持 Markdown 格式的 function schema
- 确保 skill.md 中的 YAML frontmatter 被正确解析
- 如果 function calling 未触发，尝试明确说出工具名称如 "query_device"

---

## ChatGPT

### 方法一：Custom Instructions（自定义指令）

适合个人使用，无需创建 GPT。

1. 打开 ChatGPT → 点击头像 → **Custom Instructions**
2. 在 "How would you like ChatGPT to respond?" 中粘贴 `skill.md` 的 Prompt 区内容
3. 在 "What would you like ChatGPT to know about you?" 中填入：
   ```
   我有 insentek 物联网设备，appid: xxx, secret: yyy
   ```
4. 保存后开始新对话

**限制：** ChatGPT 的 Custom Instructions 不支持真正的 function calling，API 调用需要手动复制 URL 或在插件中配置。

### 方法二：创建 GPT（推荐）

需要 ChatGPT Plus 订阅。

1. 打开 ChatGPT → **Explore GPTs** → **Create**
2. 在 Configure 标签页：
   - **Name**: Insentek Device Query
   - **Description**: 查询 insentek 物联网设备数据
   - **Instructions**: 粘贴 `skill.md` 的完整内容
3. 在 **Capabilities** 中启用 "Code Interpreter"（如需数据处理）
4. 保存并发布（可选设为 Private）

### 方法三：Actions（API 直连）

需要 ChatGPT Plus + 可访问的 API 代理。

1. 创建 GPT 时，在 Configure 页面点击 **Add actions**
2. 粘贴由 `skill.md` function schema 生成的 OpenAPI schema
3. 设置认证方式：API Key（Header: `Authorization`）
4. 保存后 GPT 可直接调用 insentek API

### 首次使用

```
User: 查看我的所有设备
```

如果已配置 appid/secret，ChatGPT 会自动认证并查询。

---

## Hermes-Agent

### 步骤

1. 打开 Hermes-Agent 管理后台
2. 进入 **Skills** → **Import**
3. 选择 `skill.md` 文件或粘贴内容
4. 配置环境变量：
   ```
   INSENTEK_BASE_URL=http://openapi.ecois.info
   ```
5. 保存并部署

### 首次使用

```
User: appid xxx secret yyy，查看设备
```

Hermes-Agent 会解析 skill.md 中的工具定义并执行对应动作。

---

## 平台兼容性速查

| 特性 | OpenClaw | Claude Code | ChatGPT (GPTs) | Hermes-Agent |
|------|----------|-------------|----------------|--------------|
| Function Schema | ✅ Native | ✅ Native | ⚠️ Via Actions | ✅ Native |
| YAML Frontmatter | ✅ | ✅ | ⚠️ | ✅ |
| Auto Token Refresh | ✅ | ✅ | ⚠️ Manual | ✅ |
| Alias Resolution | ✅ | ✅ | ✅ | ✅ |
| Time Parsing | ✅ | ✅ | ✅ | ✅ |
| Chain Calling | ✅ | ✅ | ✅ | ✅ |

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
