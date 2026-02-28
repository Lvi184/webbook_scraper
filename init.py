import os
import json
from pathlib import Path

def setup_directories():
    """创建必要的目录"""
    directories = [
        "data/uploads",
        "data/results",
        "templates",
        "logs"
    ]

    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print("创建目录: " + dir_path)

def init_config():
    """初始化配置文件"""
    config = {
        "model": "gpt-3.5-turbo",
        "chunk_size": 1000,
        "unit_size": 5,
        "max_tokens": 2000,
        "temperature": 0.7
    }

    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print("创建配置文件: config.json")

if __name__ == "__main__":
    setup_directories()
    init_config()
    print("\n初始化完成！")
    print("运行: streamlit run app.py")