#!/usr/bin/env python
"""
仿写平台启动脚本
"""

import os
import sys
import time
from pathlib import Path

def main():
    """主函数"""
    print("🚀 启动小说仿写平台...")
    print("💡 打开浏览器访问: http://localhost:8505")

    # 初始化目录
    from pathlib import Path
    for dir_path in ["data/uploads", "data/results", "templates", "logs"]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    # 启动应用
    print("📱 正在启动Web界面...")
    print("💡 打开浏览器访问: http://localhost:8505")

    # 运行Streamlit应用
    import subprocess
    subprocess.run([
        "streamlit", "run", "app_adaptation.py",
        "--server.port", "8505",
        "--server.address", "localhost",
        "--server.headless", "true"
    ])

if __name__ == "__main__":
    main()