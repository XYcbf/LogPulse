# 🩺 LogPulse - AI 驱动的日志智能分析与诊断专家

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![AI Powered](https://img.shields.io/badge/AI-DeepSeek-orange.svg)](https://www.deepseek.com/)

> **写在前面**：
> 我是一名测试工程师。在长期的职业生涯中，我深刻感受到测试工作不应只是机械的点击、单一的重复。我希望通过制作像 **LogPulse** 这样的自动化智能工具，将 AI 的力量注入到日常流程中，帮助开发者、测试人员和运维同事告别低效，更快速、更精准地定位问题根源。

---

## 📺 运行展示

### 1. 可视化主界面
*在这里插入您的 GUI 运行截图（例如：`docs/images/gui_main.png`）*
![GUI 界面展示](https://via.placeholder.com/800x450.png?text=LogPulse+GUI+Interface+Screenshot)

### 2. AI 智能诊断结果
*展示 DeepSeek AI 提供的自然语言分析建议*
![AI 分析展示](https://via.placeholder.com/800x300.png?text=AI+Root+Cause+Analysis+Display)

---

## ✨ 核心亮点

### 🧠 智能根因诊断 (Root Cause Analysis)
不再只是告诉你“发生了 10 次错误”。LogPulse 会自动提取错误堆栈和上下文，调用 DeepSeek AI 进行语义分析，以自然语言直接输出：
- **故障定性**：是权限问题、环境缺失还是代码逻辑错误？
- **深度解释**：该报错在特定系统（如 Android 或 MIUI）下的具体含义。
- **修复建议**：直接给出可操作的修改方案。

### 🚀 极致易用：为非技术人员设计
- **可视化界面**：基于 Tkinter 的直观 GUI，一键选择文件或文件夹。
- **零配置启动**：Windows 用户双击 `start.bat` 即可运行，彻底告别复杂的命令行。
- **智能 Logcat 解析**：内置强大的正则引擎，自动识别并拆分 Android Logcat 各种复杂格式（PID, TID, Tag, Level 等）。

### 📊 全方位的分析产物
分析完成后，LogPulse 会在 `rules/` 目录下自动生成：
- `root_cause_analysis.json`：AI 驱动的详细诊断建议。
- `detected_issues.json`：自动识别的潜在问题汇总。
- `generated_tdd_rules.json`：根据日志特征自动提取的测试定义。
- `test_issue_remediation_generated.py`：自动生成的 pytest 测试骨架，助力回归测试。

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
复制 `.env.example` 并重命名为 `.env`，填入您的 DeepSeek API Key：
```ini
OPENAI_API_KEY=您的_DeepSeek_API_Key
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
│   ├── gui_app.py      # 可视化界面
│   ├── log_loader.py   # 智能日志加载与解析
│   ├── issue_detector.py # 问题检测引擎
│   └── root_cause_analyzer.py # AI 根因分析器
├── rules/              # 分析结果输出目录
├── tests/              # 自动生成的测试代码
├── launcher.py         # 稳健的程序入口
├── start.bat           # Windows 一键启动脚本
└── README.md           # 本说明文档
```

---

## 🤝 贡献与反馈

我们非常欢迎任何形式的贡献！如果您有更好的正则匹配模式、更精准的 AI Prompt 建议，或者发现了 Bug，欢迎提交 Issue 或 Pull Request。

## 📄 开源协议

本项目采用 [MIT](LICENSE) 协议开源。

---
*Powered by DeepSeek AI - 让日志分析更有温度。*
