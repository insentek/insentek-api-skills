# Pitfalls Research

**Domain:** Agent Skill for IoT Device Data API
**Researched:** 2026-05-13
**Confidence:** HIGH

## Critical Pitfalls

### Pitfall 1: API 描述与实际接口不一致

**What goes wrong:**
skill.md 中描述的 API 参数、路径或响应格式与实际的 insentek OpenAPI 不一致，导致 Agent 调用失败。

**Why it happens:**
- 手工编写时凭记忆而非对照文档
- API 文档更新后 skill.md 未同步
- 复制粘贴时参数类型描述错误

**How to avoid:**
- 严格对照 `ref/api-document-latest.pdf` 和 `ref/api-repo/` 源码编写
- 每个 API 描述后标注来源文档页码/源码位置
- 编写后用实际 API 响应验证示例

**Warning signs:**
- 示例中的请求参数与实际 API 不匹配
- 响应示例缺少实际返回的关键字段
- 用户反馈"调用失败"或"返回 404"

**Phase to address:**
Phase 1（API 接口梳理与 skill 骨架编写）

---

### Pitfall 2: Skill 过于复杂导致 Agent 无法正确选择工具

**What goes wrong:**
定义了太多 tools/function，Agent 在面对用户查询时选择错误的工具，或频繁在多个工具间切换。

**Why it happens:**
- 将每个 API endpoint 都定义为独立 tool（过度拆分）
- Tool 描述模糊，Agent 无法区分使用场景
- 缺少 tool 选择的明确指导

**How to avoid:**
- 按功能聚合 API（如"设备查询"聚合列表+详情）
- 每个 tool 描述明确使用场景和前置条件
- 在 interaction patterns 中写明"何时使用哪个 tool"

**Warning signs:**
- Agent 对同一类查询使用不同 tool
- 用户需要反复澄清才能得到正确结果
- 对话中频繁出现 tool 切换

**Phase to address:**
Phase 1（Tool 设计与聚合）

---

### Pitfall 3: 忽视平台差异导致兼容性问题

**What goes wrong:**
skill.md 在某些平台工作正常，在其他平台解析错误或行为异常。

**Why it happens:**
- 使用了平台-specific 的 Markdown 扩展
- YAML frontmatter 格式不兼容
- Function schema 使用了非标准特性

**How to avoid:**
- 使用最小公共子集的 Markdown 语法
- 验证 YAML frontmatter 在所有目标平台可解析
- 在至少 2 个目标平台上测试 skill 行为

**Warning signs:**
- 在某平台上 skill 未被识别
- 格式化输出在某平台显示异常
- 工具调用在某平台失效

**Phase to address:**
Phase 2（跨平台测试与适配）

---

### Pitfall 4: 输出格式不友好

**What goes wrong:**
Agent 返回的数据呈现方式让用户难以理解（大段 JSON、无格式文本、缺少上下文）。

**Why it happens:**
- skill.md 中未定义输出格式规范
- 缺少数据转 human-readable 的明确指令
- 假设用户能看懂原始数据

**How to avoid:**
- 在 skill.md 中明确定义"输出必须遵循的格式"
- 提供输出模板（表格、摘要、报告格式）
- 在 examples 中展示良好的输出格式

**Warning signs:**
- 用户反馈"看不懂"
- 输出是未格式化的 JSON
- 数据缺少单位、时间戳等上下文

**Phase to address:**
Phase 1（输出格式定义）和 Phase 3（示例完善）

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| 跳过平台测试 | 节省时间 | 用户在某平台无法使用 | 仅内部预览版，正式版必须测试 |
| 硬编码示例数据 | 快速产出示例 | 示例与实际 API 不符 | 标注为"示意数据"，正式版替换 |

## "Looks Done But Isn't" Checklist

- [ ] **API 覆盖:** 是否遗漏了 `ref/api-repo/` 中的某个 endpoint？
- [ ] **参数准确性:** 每个 API 的参数类型、必填/可选是否与实际一致？
- [ ] **认证说明:** 是否清楚说明了如何获取和配置 API 密钥？
- [ ] **错误处理:** 是否说明了常见错误码和应对方式？
- [ ] **平台兼容:** 是否在至少 2 个目标平台验证过？

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| API 描述不一致 | Phase 1 | 对照源码和文档逐条核对 |
| Tool 过度拆分 | Phase 1 | 用示例查询验证 tool 选择正确性 |
| 平台兼容性 | Phase 2 | 在 OpenClaw + Claude Code 双平台测试 |
| 输出不友好 | Phase 1+3 | 用户走查示例对话，确认输出可读 |

---
*Pitfalls research for: Agent Skill for IoT Device Data API*
*Researched: 2026-05-13*
