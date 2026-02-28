#!/usr/bin/env python
"""
网文拆书平台启动脚本
"""

import subprocess
import sys
import time

def check_requirements():
    """检查依赖是否安装"""
    required_packages = [
        'streamlit',
        'pdfplumber',
        'python-docx',
        'jieba',
        'openai'
    ]

    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"缺少以下依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False

    return True

def main():
    """主函数"""
    print("🚀 启动网文拆书平台...")

    # 检查依赖
    # if not check_requirements():
    #     sys.exit(1)

    # 初始化目录
    from pathlib import Path
    for dir_path in ["data/uploads", "data/results", "templates", "logs"]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    # 启动应用
    print("📱 正在启动Web界面...")
    print("💡 打开浏览器访问: http://localhost:8503")

    # 运行Streamlit应用
    subprocess.run([
        "streamlit", "run", "app.py",
        "--server.port", "8503",
        "--server.address", "localhost",
        "--server.headless", "true"
    ])

if __name__ == "__main__":
    main()