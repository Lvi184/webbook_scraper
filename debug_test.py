#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
调试脚本 - 测试LLM客户端初始化
"""

import sys
import traceback
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

try:
    from services.llm_client import LLMClient
    print("LLMClient导入成功")

    # 测试初始化
    api_key = "sk-5576ad8298a94cad80c1a87dfa32e4d3"
    provider = "openai"
    model = "qwen-turbo"

    print(f"正在初始化 LLMClient: {provider}/{model}")

    llm_client = LLMClient(api_key, provider, model)
    print("LLMClient初始化成功")

    # 测试生成
    test_prompt = "请简单介绍一下自己"
    print(f"测试生成: {test_prompt}")

    response = llm_client.generate(test_prompt)
    print(f"生成成功: {response[:100]}...")

except Exception as e:
    print(f"错误: {str(e)}")
    print("错误详情:")
    traceback.print_exc()