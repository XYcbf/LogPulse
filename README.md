# 🩺 LogPulse - 日志智能分析与诊断工具

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![AI Powered](https://img.shields.io/badge/AI-DeepSeek-orange.svg)](https://www.deepseek.com/)

**LogPulse** 是一款专为开发者、测试人员和运维专家打造的轻量级、可视化日志诊断引擎。
它彻底改变了传统工具只能“机械统计”的现状：通过内置的解析算法，LogPulse 能从纷繁复杂的原始日志中自动识别并锁定报错点，精准提取错误堆栈及上下文信息。 在完成这些核心的数据清洗与特征定位后，它深度结合 DeepSeek AI 的语义分析能力，为你直观呈现故障的根本原因与解决方案。
## 📺 运行展示
**LogPulse** 界面采用极简风格，将复杂的工程逻辑深藏于后台。坚持“零门槛”交互逻辑：用户只需选择路径并点击“智能分析”，LogPulse 即可自动完成从日志定位、特征提取到 AI 诊断的全流程，将海量原始数据转化为直观的高亮诊断清单。

### 1. 可视化主界面
<img width="1189" height="934" alt="image" src="https://github.com/user-attachments/assets/409537af-0628-4a66-9f03-455d35c43f16" />


### 2. AI 智能诊断结果
*展示 DeepSeek AI 提供的结构化分析建议*
<img width="1881" height="838" alt="image" src="https://github.com/user-attachments/assets/7acf0300-0c50-49ed-84fa-a022ef20d053" />
<img width="1867" height="612" alt="image" src="https://github.com/user-attachments/assets/8f2f3ded-894c-4b68-ac2d-8d005ac6b122" />


---

## ✨ 核心亮点

### 🧠 深度根因诊断 (Root Cause Analysis)
不再只是简单地罗列“错误次数”。LogPulse 能够从海量日志中自动捕获关键异常，精准提取错误堆栈与上下文关联信息；随后，它将这些结构化情报交由 DeepSeek AI 进行深度语义分析，并严格按照以下标准输出：
- **故障定性**：直接判断是权限问题、环境缺失还是代码逻辑错误。
- **深度解释**：详细阐述报错在特定系统（如 Android 或 MIUI）下的具体含义及技术背景。
- **修复建议**：提供精准、可操作的修改方案（如检查清单或代码片段）。

### 🚀 极致易用：为非技术人员设计
- **可视化界面**：基于 Tkinter 的直观 GUI，支持一键选择文件或文件夹。
- **零配置启动**：Windows 用户双击 `start.bat` 即可运行，彻底告别复杂的命令行。
- **智能 Logcat 解析**：内置强大的正则引擎，自动识别并拆分 Android Logcat 各种复杂格式（PID, TID, Tag, Level 等）。

### 📊 全方位的分析产物
分析完成后，LogPulse 会在 `rules/` 目录下自动生成：
- `root_cause_analysis.json`：AI 驱动的详细诊断建议。
- `detected_issues.json`：自动识别的潜在问题汇总。
- `generated_tdd_rules.json`：根据日志特征自动提取的测试定义。
- `test_issue_remediation_generated.py`：自动生成的 pytest 测试骨架。

---

## 🛠️ 自动化 TDD 工作流

LogPulse 不仅仅是一个分析工具，它还构建了一套**从日志到测试 (Log-to-Test)** 的完整闭环，赋能测试驱动开发：

1. **自动生成规则**：分析日志时，系统会自动提取异常模式并固化为 `generated_tdd_rules.json` 规则库。
2. **合成测试代码**：系统根据规则库，自动生成基于 `pytest` 的测试代码 `test_issue_remediation_generated.py`。
3. **一键执行验证**：
   你可以直接运行以下命令来验证系统对已知问题的识别能力：
   ```bash
   pytest tests/test_issue_remediation_generated.py
   ```
4. **回归守卫**：当你优化了解析算法或升级了 AI 提示词，通过运行这些自动生成的测试，可以确保系统不会产生“功能退化”，始终保持对已知故障的精准识别。
5. 详情见《LogPulse 自动化 TDD 实践手册》即TDD_MANUAL.md文档
---


## 🛠️ 支持格式

| 格式类型 | 扩展名 | 说明 |
| :--- | :--- | :--- |
| **结构化日志** | `.json`, `.jsonl` | 自动识别对象数组或单行 JSON |
| **数据库日志** | `.db`, `.sqlite` | 自动扫描所有数据表并提取日志记录 |
| **纯文本/Logcat** | `.log`, `.txt` | **深度优化**：支持各种变体格式的自动字段拆分 |

---


## 🏃 快速开始
### 1. 准备环境
确保您的系统已安装 **Python 3.10** 或更高版本。
### 2. 安装依赖
克隆项目后，在根目录运行：
```bash
pip install -r requirements.txt
```
### 3. 配置 AI（开启超能力 🦸）
直接打开项目根目录下的 `.env` 文件，填入您的 DeepSeek API Key：
```ini
OPENAI_API_KEY=在这里填入您的_DeepSeek_API_Key
OPENAI_BASE_URL=https://api.deepseek.com
```
### 4. 运行
- **Windows (推荐)**：直接双击 `start.bat`。
- **通用方式**：运行 `python launcher.py`。


---

## 📂 项目结构

```text
LogPulse/
├── src/                # 核心逻辑
│   ├── gui_app.py      # 可视化界面（富文本排版优化）
│   ├── log_loader.py   # 智能日志加载与解析（支持正则 Logcat）
│   ├── issue_detector.py # 问题检测引擎
│   └── root_cause_analyzer.py # AI 根因分析器（DeepSeek 集成）
├── rules/              # 分析结果输出目录
├── tests/              # 自动生成的测试代码
├── launcher.py         # 稳健的 Python 程序入口
├── start.bat           # Windows 一键启动脚本
├── .env                # 个人配置文件（不上传 GitHub）
└── README.md           # 本说明文档
```

---

## 🤝 贡献与反馈

我们非常欢迎任何形式的贡献！如果您有更好的正则匹配模式、更精准的 AI Prompt 建议，或者发现了 Bug，欢迎提交 Issue 或 Pull Request。

## 📄 开源协议

本项目采用 [MIT](LICENSE) 协议开源。

---

> **💡 开发者的寄语**：
> 作为一名测试工程师，我始终坚信测试的价值不应被枯燥的机械操作所埋没。我打造LogPulse 的初衷，是希望将 AI 算法深度植入生产流，
> 用智能化的利刃打破低效循环。让开发者、测试及运维团队从重复性劳动中解脱，赋予每位同行极速洞察、精准溯源的能力。

---
*Powered by DeepSeek AI - 让日志分析更有温度。*
