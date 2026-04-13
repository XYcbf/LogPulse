# LogPulse - 日志智能分析工具

LogPulse 是一款专为开发者和运维人员设计的轻量级日志分析工具。它结合了传统的规则匹配与先进的 AI (DeepSeek) 技术，能够自动从海量日志中提取关键错误信息，并直接给出自然的根因分析建议。

## 🌟 核心特性

- **可视化操作**：提供直观的 GUI 界面，支持一键选择文件或文件夹进行分析。
- **智能根因分析**：集成 DeepSeek AI，不再只是枯燥的日志统计，AI 会直接告诉你“为什么报错”以及“如何修复”。
- **全格式兼容**：
  - **结构化日志**：支持 JSON, JSONL 格式。
  - **数据库日志**：支持 SQLite (.db, .sqlite) 文件。
  - **文本日志**：支持任意文本格式，特别针对 Android Logcat 进行了正则优化解析。
- **一键启动**：专为 Windows 用户优化，双击 `start.bat` 即可运行，无需复杂的命令行操作。
- **自动化产物**：分析完成后自动生成排查报告、TDD 规则以及 pytest 测试骨架。

## 🚀 快速开始

### 1. 环境要求
- Python 3.10+
- Windows 系统 (推荐使用内置的 `start.bat`)

### 2. 安装依赖
在项目根目录下打开终端，运行：
```bash
pip install -r requirements.txt
```

### 3. 配置 AI 密钥 (可选但强烈推荐)
为了使用 AI 智能分析功能，请将您的 DeepSeek API Key 填入 `.env` 文件（可参考 `.env.example`）：
```text
OPENAI_API_KEY=您的_DeepSeek_API_Key
OPENAI_BASE_URL=https://api.deepseek.com
```

### 4. 运行
- **方法 A (推荐)**：双击根目录下的 `start.bat`。
- **方法 B (命令行)**：
  ```bash
  python launcher.py
  ```

## 📂 项目结构
- `src/`：核心源代码（GUI、解析器、AI 分析器等）。
- `rules/`：分析产物（规则、排查报告、根因分析结果）。
- `tests/`：自动生成的测试骨架。
- `launcher.py`：稳健的程序入口。
- `start.bat`：Windows 一键启动脚本。

## 🛠️ 如何贡献
1. Fork 本仓库。
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)。
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)。
4. 推送到分支 (`git push origin feature/AmazingFeature`)。
5. 开启一个 Pull Request。

## 📄 开源协议
本项目采用 [MIT](LICENSE) 协议开源。
