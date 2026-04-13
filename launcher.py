import os
import sys
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv # 导入 load_dotenv

# 将项目根目录添加到 Python 路径，确保能找到 src 包
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# 显式加载 .env 文件，确保环境变量被正确设置
dotenv_path = os.path.join(project_root, '.env')
load_dotenv(dotenv_path)

if __name__ == "__main__":
    print("LogPulse Initializing...")
    print("正在启动 LogPulse 可视化分析工具...")
    try:
        from src.gui_app import LogAnalysisApp
        root = tk.Tk()
        app = LogAnalysisApp(root)
        root.mainloop()
    except ImportError as e:
        print(f"Error: Could not find project modules. {e}")
        messagebox.showerror("启动错误", f"无法加载项目模块：{e}\n请确保已安装依赖：pip install -r requirements.txt")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        messagebox.showerror("启动错误", f"发生意外错误：{e}")
