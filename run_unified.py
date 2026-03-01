#!/usr/bin/env python
"""
启动整合系统 - 拆书仿写一体化平台
"""

import subprocess
import time

# 启动Streamlit应用
print("🚀 启动拆书仿写一体化平台...")
print("📱 正在启动Web界面...")
print("💡 打开浏览器访问: http://localhost:8511")

# 运行Streamlit应用
subprocess.run([
    "streamlit", "run", "app_unified.py",
    "--server.port", "8511",
    "--server.address", "localhost",
    "--server.headless", "true"
])
