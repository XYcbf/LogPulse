import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import os
import json
import threading
from pathlib import Path
from src.issue_detector import detect_log_issues
from src.remediation_planner import build_remediation_plan, generate_issue_pytest_skeleton
from src.rule_generator import generate_tdd_rules
from src.root_cause_analyzer import analyze_root_cause

class LogAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LogPulse - 日志智能分析工具")
        self.root.geometry("800x600")
        
        # 尝试从环境变量获取 DeepSeek Key
        if "OPENAI_API_KEY" not in os.environ:
            # 如果没有设置，可以提醒用户在启动前设置环境变量
            pass
        
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
        self.result_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, font=("Consolas", 10), bg="#f4f4f4")
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

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
        self.result_text.insert(tk.END, ">>> 正在初始化分析引擎...\n")
        
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

            self.update_log(">>> 正在生成 TDD 规则...\n")
            generate_tdd_rules(log_dir, rules_output)
            
            self.update_log(">>> 正在检测日志问题...\n")
            report = detect_log_issues(log_dir, report_output)
            
            self.update_log(">>> 正在请求 DeepSeek AI 进行根因分析...\n")
            analysis = analyze_root_cause(report)
            
            # 显示 AI 结果
            self.update_log(f"\n{'='*40}\n")
            self.update_log(f"{analysis['summary']}\n")
            for detail in analysis['details']:
                self.update_log(f"\n{detail}\n")
            self.update_log(f"{'='*40}\n")

            self.update_log(">>> 正在生成修复计划...\n")
            plan = build_remediation_plan(report, plan_output)
            generate_issue_pytest_skeleton(plan, pytest_output)
            
            self.update_log("\n>>> 分析完成！结果已保存至 rules/ 文件夹。")
            messagebox.showinfo("完成", "日志分析已完成！")

        except Exception as e:
            self.update_log(f"\n[错误] 分析过程中出现异常: {str(e)}")
            messagebox.showerror("错误", f"分析失败: {str(e)}")
        finally:
            self.root.after(0, lambda: self.btn_run.config(state=tk.NORMAL, text="开始智能分析"))

    def update_log(self, text):
        self.root.after(0, lambda: self.result_text.insert(tk.END, text))
        self.root.after(0, lambda: self.result_text.see(tk.END))

if __name__ == "__main__":
    root = tk.Tk()
    app = LogAnalysisApp(root)
    root.mainloop()
