#!/usr/bin/env python
"""
拆书分析测试脚本
"""

import os
import json
from pathlib import Path
from services.file_parser import FileParser
from services.llm_client import LLMClient
from services.book_analyzer import BookAnalyzer

def test_analysis():
    """测试拆书分析功能"""
    print("🚀 开始拆书分析测试...")
    
    # 1. 输入API密钥
    api_key = "sk-cd50e38e3208480f9b892e2a861e908c"
    
    # 2. 选择模型
    provider = "openai"
    model = "qwen-turbo"
    
    # 3. 初始化LLM客户端
    print("初始化LLM客户端...")
    llm_client = LLMClient(api_key, provider, model)
    
    # 4. 选择要分析的文件
    upload_dir = Path("data/uploads")
    if not upload_dir.exists():
        print("❌ 上传文件目录不存在")
        return
    
    # 列出可用的文件
    files = list(upload_dir.glob("*.*"))
    if not files:
        print("❌ 没有找到上传的文件")
        return
    
    print("\n可用的文件:")
    for i, file in enumerate(files):
        print(f"{i+1}. {file.name}")
    
    # 选择文件
    choice = int(input("请选择要分析的文件编号: ")) - 1
    if choice < 0 or choice >= len(files):
        print("❌ 无效的选择")
        return
    
    file_path = files[choice]
    print(f"\n分析文件: {file_path.name}")
    
    # 5. 解析文件
    print("解析文件...")
    file_parser = FileParser()
    file_data = file_parser.parse_file(str(file_path))
    
    print(f"检测到章节数: {len(file_data['chapters'])}")
    
    # 6. 执行拆书分析
    print("开始拆书分析...")
    book_analyzer = BookAnalyzer(llm_client)
    
    try:
        analysis_result = book_analyzer.analyze_book(file_data)
        print("✅ 拆书分析完成！")
        
        # 7. 保存分析结果
        analysis_dir = Path("data/analysis")
        analysis_dir.mkdir(exist_ok=True, parents=True)
        
        output_file = analysis_dir / f"{file_path.stem}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 分析结果已保存到: {output_file}")
        print(f"\n分析结果摘要:")
        print(f"- 章节数: {analysis_result['book_info']['total_chapters']}")
        print(f"- 剧情单元: {analysis_result['book_info']['total_units']}")
        print(f"- 角色数: {len(analysis_result['stage2_characters'])}")
        
    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")

if __name__ == "__main__":
    test_analysis()
