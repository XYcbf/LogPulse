import os
import json
import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from dotenv import load_dotenv # 导入 load_dotenv

from src.issue_detector import detect_log_issues
from src.remediation_planner import build_remediation_plan, generate_issue_pytest_skeleton
from src.rule_generator import generate_tdd_rules
from src.root_cause_analyzer import analyze_root_cause

class LogAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LogPulse - 日志智能分析工具")
        self.root.geometry("800x600")
        
        # 在 GUI 应用启动时加载 .env 文件
        load_dotenv()
        
        # 尝试从环境变量获取 DeepSeek Key
        if "OPENAI_API_KEY" not in os.environ:
            messagebox.showwarning(
                "AI Key 未配置",
                "未检测到 OPENAI_API_KEY 环境变量。\n"
                "AI 智能分析功能将无法使用，请在项目根目录创建 .env 文件并配置您的 DeepSeek API Key。"
            )
        
        self.setup_ui()

    def setup_ui(self):
        # 顶部：路径选择
        top_frame = tk.Frame(self.root, pady=20)
        top_frame.pack(fill=tk.X)

        tk.Label(top_frame, text="日志路径:", font=("Arial", 10)).pack(side=tk.LEFT, padx=10)
        
        self.path_entry = tk.Entry(top_frame, font=("Arial", 10))
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        btn_browse_file = tk.Button(top_frame, text="选择文件", command=self.browse_file)
        btn_browse_file.pack(side=tk.LEFT, padx=5)
        
        btn_browse_dir = tk.Button(top_frame, text="选择文件夹", command=self.browse_directory)
        btn_browse_dir.pack(side=tk.LEFT, padx=5)

        # 中部：操作按钮
        mid_frame = tk.Frame(self.root, pady=10)
        mid_frame.pack(fill=tk.X)
        
        self.btn_run = tk.Button(mid_frame, text="开始智能分析", command=self.start_analysis_thread, 
                                 bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), height=2)
        self.btn_run.pack(pady=10)

        # 底部：结果展示
        tk.Label(self.root, text="分析结果 (DeepSeek AI 智能建议):", font=("Arial", 10, "bold")).pack(anchor=tk.W, padx=10)
        self.result_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("微软雅黑", 10), bg="#FFFFFF")
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 配置文本标签样式
        self.result_text.tag_config("title", foreground="#1A237E", font=("微软雅黑", 11, "bold"))
        self.result_text.tag_config("sample_header", foreground="#455A64", font=("微软雅黑", 10, "bold"), spacing1=10)
        self.result_text.tag_config("fault_type", foreground="#D32F2F", font=("微软雅黑", 10, "bold"))
        self.result_text.tag_config("explanation", foreground="#388E3C", font=("微软雅黑", 10, "bold"))
        self.result_text.tag_config("remediation", foreground="#1976D2", font=("微软雅黑", 10, "bold"))
        self.result_text.tag_config("system_info", foreground="#757575", font=("微软雅黑", 9, "italic"))
        self.result_text.tag_config("separator", foreground="#BDBDBD")

    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, file_path)

    def browse_directory(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, dir_path)

    def start_analysis_thread(self):
        path = self.path_entry.get().strip()
        if not path:
            messagebox.showwarning("警告", "请先选择日志文件或文件夹！")
            return
        
        self.btn_run.config(state=tk.DISABLED, text="正在分析中，请稍候...")
        self.result_text.delete(1.0, tk.END)
        self.update_styled_log(">>> 正在初始化分析引擎...\n", "system_info")
        
        # 开启线程运行，避免 GUI 卡死
        threading.Thread(target=self.run_analysis, args=(path,), daemon=True).start()

    def run_analysis(self, log_path):
        try:
            log_dir = Path(log_path)
            project_root = Path(__file__).resolve().parents[1]
            output_dir = project_root / "rules"
            tests_dir = project_root / "tests"
            
            rules_output = output_dir / "generated_tdd_rules.json"
            report_output = output_dir / "detected_issues.json"
            plan_output = output_dir / "remediation_plan.json"
            pytest_output = tests_dir / "test_issue_remediation_generated.py"

            self.update_styled_log(">>> 正在生成 TDD 规则...\n", "system_info")
            generate_tdd_rules(log_dir, rules_output)
            
            self.update_styled_log(">>> 正在检测日志问题...\n", "system_info")
            report = detect_log_issues(log_dir, report_output)
            
            self.update_styled_log(">>> 正在请求 DeepSeek AI 进行根因分析...\n", "system_info")
            analysis = analyze_root_cause(report)
            
            # 渲染智能分析结果
            self.render_ai_analysis(analysis)

            self.update_styled_log("\n>>> 正在生成修复计划...\n", "system_info")
            plan = build_remediation_plan(report, plan_output)
            generate_issue_pytest_skeleton(plan, pytest_output)
            
            self.update_styled_log("\n>>> 分析完成！结果已保存至 rules/ 文件夹。", "title")
            messagebox.showinfo("完成", "日志分析已完成！")

        except Exception as e:
            self.update_styled_log(f"\n[错误] 分析过程中出现异常: {str(e)}", "fault_type")
            messagebox.showerror("错误", f"分析失败: {str(e)}")
        finally:
            self.root.after(0, lambda: self.btn_run.config(state=tk.NORMAL, text="开始智能分析"))

    def render_ai_analysis(self, analysis):
        """解析 AI 文本并进行富文本渲染。"""
        self.update_styled_log(f"\n{analysis['summary']}\n", "title")
        
        full_text = "".join(analysis['details'])
        # 按样本进行粗略切分渲染
        parts = full_text.split("--- 错误样本 ---")
        for part in parts:
            if not part.strip(): continue
            
            self.update_styled_log("-" * 60 + "\n", "separator")
            self.update_styled_log("【 错误样本 】\n", "sample_header")
            
            lines = part.strip().split("\n")
            for line in lines:
                if line.startswith("故障定性："):
                    self.update_styled_log("● " + line + "\n", "fault_type")
                elif line.startswith("深度解释："):
                    self.update_styled_log("● " + line + "\n", "explanation")
                elif line.startswith("修复建议："):
                    self.update_styled_log("● " + line + "\n", "remediation")
                elif line.strip():
                    # 样本内容或普通文本
                    self.update_styled_log(line + "\n")

    def update_styled_log(self, text, tag=None):
        """支持样式的日志更新。"""
        def append():
            self.result_text.insert(tk.END, text, tag)
            self.result_text.see(tk.END)
        self.root.after(0, append)

if __name__ == "__main__":
    root = tk.Tk()
    app = LogAnalysisApp(root)
    root.mainloop()
