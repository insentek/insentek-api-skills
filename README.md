# Insentek OpenAPI Skill

> 让终端用户用自然语言轻松查询 insentek（东方智感）物联网设备数据。

---

## 简介

本项目基于 insentek OpenAPI v3，产出一份通用 `skill.md` 技能文件及配套文档与示例。终端用户可在 **OpenClaw、Hermes-Agent、Claude Code、ChatGPT** 等 Agent 平台上直接对话使用，通过自然语言调用 API 完成设备数据查询、报告生成与实时分析。

**支持的设备类型：**
- 🌱 **Z** — 土壤墒情仪（土壤温度、水分、电导率）
- 🌤️ **T** — 气象站（空气温度、湿度、风速、降雨量、PM2.5 等）
- 📏 **J** — 见厘液位计（激光液位、电池电压）

---

## 快速开始

### 1. 获取认证信息

登录 [E 生态](https://www.ecois.info)，在「应用管理」中创建应用，获取 `appid` 和 `secret`。

### 2. 安装 Skill

| 平台 | 安装方式 | 卸载 |
|------|---------|------|
| **OpenClaw** | `clawhub skill install insentek-api-skill` | `clawhub skill remove insentek-api-skill` |
| **Claude Code** | 项目根目录放 `skill.md` 或 `/load skill.md` | 删除文件或 `/clear` |
| **ChatGPT** | GPTs Instructions 粘贴 / Actions Schema 导入 | Delete GPT / 删除 Action |
| **Hermes-Agent** | `~/.hermes/skills/` 目录下放 skill 文件 | `rm` 文件后 `reload` |

> 各平台分操作系统（Windows / macOS / Linux）的详细安装路径、ClawHub 安装命令、卸载步骤见 [`docs/platform-setup.md`](docs/platform-setup.md)。

### 3. 开始对话

```
User: 我的 appid 是 xxx，secret 是 yyy，查看所有设备
```

更多用法见 [`docs/getting-started.md`](docs/getting-started.md)。

---

## 项目结构

```
.
├── skill.md                     # 核心技能文件
├── docs/
│   ├── getting-started.md       # 快速开始指南
│   ├── platform-setup.md        # 各平台配置指南
├── reference/
│   └── api-doc.md               # 完整 API 文档 (OpenAPI v3.1.9)
├── examples/
│   ├── queries.md               # 查询类对话示例
│   ├── reports.md               # 报告生成示例
│   └── alerts.md                # 异常分析示例
├── scripts/                     # 参考实现脚本
│   ├── insentek_cli.py          # 统一 CLI（认证/查询/导出）
│   ├── export_excel.py          # Excel 导出
│   └── README.md                # 脚本使用说明
├── PLATFORM-TEST.md             # 跨平台测试计划（自检清单）
├── ref/                         # 参考材料（API 仓库 + 文档）
│   ├── api-repo/                # Spring Boot API 源码
│   └── api-document-latest.pdf  # 官方接口文档
└── .planning/                   # 项目规划文档
    ├── PROJECT.md
    ├── REQUIREMENTS.md
    ├── ROADMAP.md
    ├── STATE.md
    └── phases/
        ├── 01-api-interface-mapping/
        ├── 02-skill-core/
        ├── 03-documentation/
        ├── 04-examples/
        └── 05-platform-test/
```

---

## 核心功能

| 功能 | 说明 |
|------|------|
| 🔐 自动认证 | appid+secret → token，自动缓存与刷新 |
| 📋 设备管理 | 列表查询、别名解析、单设备详情 |
| 📊 数据查询 | 实时/历史/指定时刻/增量同步 |
| 🧠 智能推断 | 自然语言时间自动解析（"上周"→日期范围） |
| 🔗 链式调用 | alias → SN → 数据，自动串联 |
| 📈 趋势分析 | 平均值/最大值/最小值/变化率自动计算 |
| ⚖️ 跨设备对比 | 并排比较 + 差异高亮 |
| ⚠️ 异常检测 | 电池过低、水分异常、温度突变自动标记 |
| 🏭 多行业适配 | Z/T/J 设备类型自动识别与参数翻译 |
| 🎯 意图确认 | 输出形式不明确时自动询问（查看/导出/报告） |
| 🛡️ 查询边界 | 最大1年/3年回溯/5万条导出上限，超限自动拦截 |
| 📤 数据导出 | CSV / Excel / JSON / HTML 报告一键生成 |
| 🔍 环境检查 | 首次使用前自动检查 Python、脚本、依赖、API 可达性 |

---

## 对话示例

**查看设备列表**
```
User: 查看我的设备
Agent: 📋 设备列表（共 3 台）...
```

**查询实时数据**
```
User: 1号大棚现在的温度
Agent: 📍 1号大棚 — 10cm: 18.5℃, 20cm: 17.2℃ ...
```

**历史趋势**
```
User: 最近7天的土壤湿度变化
Agent: 📊 趋势表格 + 平均/最高/最低/变化率小结
```

**异常检测**
```
User: 检查所有设备的电池
Agent: 🔋 巡检报告 — 2号大棚 2.85V 🔴 过低
```

更多示例见 [`examples/`](examples/)。

---

## 时间表达支持

| 你说 | Agent 理解 |
|------|-----------|
| "现在" / "最新" / "实时" | 调用 /latest |
| "昨天" / "上周" / "本月" | 自动计算 YYYYMMDD,YYYYMMDD |
| "最近7天" / "近一周" | 过去 7 天 |
| "12点30分" / "某时刻" | 调用 /moment/{datetime} |
| "同步" / "增量" | 调用 /incremental |
| *(没提时间)* | 默认最近 24 小时 |

---

## 平台兼容性

| 特性 | OpenClaw | Claude Code | ChatGPT | Hermes-Agent |
|------|:--------:|:-----------:|:-------:|:------------:|
| Function Schema | ✅ | ✅ | ⚠️ Actions | ✅ |
| 自动 Token 刷新 | ✅ | ✅ | ⚠️ | ✅ |
| 别名解析 | ✅ | ✅ | ✅ | ✅ |
| 时间推断 | ✅ | ✅ | ✅ | ✅ |
| 链式调用 | ✅ | ✅ | ✅ | ✅ |

⚠️ = 需额外配置（详见 [`docs/platform-setup.md`](docs/platform-setup.md)）

---

## API 参考

- **Base URL**: `http://openapi.ecois.info`
- **认证**: `GET /v3/token?appid={appid}&secret={secret}`
- **设备**: `/v3/devices`, `/v3/device/{sn}`, `/v3/device/{sn}/description`
- **数据**: `/v3/device/{sn}/data`, `/latest`, `/moment/{datetime}`, `/incremental`

完整参数说明见 [`reference/api-doc.md`](reference/api-doc.md)。

---

## 版本

- **当前版本**: v1.1.0
- **API 版本**: insentek OpenAPI v3
- **更新日期**: 2026-05-22

---

## 贡献

本项目为内容产出型项目，主要交付物为 `skill.md` 及配套文档。

如需反馈问题或建议：
1. 检查 [`PLATFORM-TEST.md`](PLATFORM-TEST.md) 确认是否为已知限制
2. 提交 issue 到项目仓库

---

## 许可证

待定 / 请参考 insentek 官方使用条款

---

*Generated with Claude Code · 基于 insentek OpenAPI v3*
