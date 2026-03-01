#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
完整测试脚本 - 模拟拆书流程
"""

import sys
import json
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(str(Path(__file__).parent))

def test_book_analysis():
    """测试完整的拆书流程"""
    try:
        from services.file_parser import FileParser
        from services.text_processor import TextProcessor
        from services.book_analyzer import BookAnalyzer
        from services.llm_client import LLMClient

        print("=== 网文拆书流程测试 ===\n")

        # 1. 初始化LLM客户端
        print("1. 初始化LLM客户端...")
        api_key = "sk-xxxxx"
        provider = "qwen"  # 使用qwen提供商
        model = "qwen-turbo"

        llm_client = LLMClient(api_key, provider, model)
        print(f"使用模型: {provider}/{model}")

        # 2. 解析文件
        print("\n2. 解析文件...")
        file_parser = FileParser()
        file_path = r"data\uploads\novel_617058.docx"
        # file_path = "data/uploads/西游记上卷.txt"
        file_data = file_parser.parse_file(file_path)

        print(f"文件名: {file_data['filename']}")
        print(f"检测到章节: {file_data['total_chapters']}章")

        # 显示章节信息
        for i, chapter in enumerate(file_data['chapters']):
            print(f"第{i+1}章: {chapter['title']} ({len(chapter['content'])}字)")

        # 3. 文本处理
        print("\n3. 文本处理...")
        text_processor = TextProcessor()
        units = text_processor.split_into_units(file_data['chapters'], unit_size=1)

        print(f"创建了{len(units)}个剧情单元")
        for unit in units:
            print(f"单元{unit['unit_number']}: 第{unit['chapter_range'][0]}章 - {unit['theme']}")

        # 4. 执行分析（只测试第一单元，节省时间）
        print("\n4. 执行分析...")
        analyzer = BookAnalyzer(llm_client)

        # 只分析第一单元用于测试
        test_file_data = {
            'chapters': file_data['chapters'][:1],
            'filename': file_data['filename']
        }

        result = analyzer.analyze_book(test_file_data)

        print("\n分析完成！")
        print(f"处理了{len(result['stage1_units'])}个单元")
        print(f"生成了世界观总纲")
        print(f"生成了{len(result['stage2_characters'])}个角色设定")

        # 5. 保存结果
        output_file = "test_analysis_result.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n结果已保存到: {output_file}")

        # 6. 显示部分结果
        print("\n=== 世界观总纲示例 ===")
        if 'stage2_world_outline' in result:
            world_outline = result['stage2_world_outline']
            if isinstance(world_outline, dict):
                for key, value in world_outline.items():
                    print(f"{key}: {str(value)[:100]}...")

        print("\n=== 角色设定示例 ===")
        if 'stage2_characters' in result and result['stage2_characters']:
            character = result['stage2_characters'][0]
            if isinstance(character, dict):
                print(f"角色名: {character.get('name', '未知')}")
                print(f"属性标签: {character.get('属性标签', '未知')}")

        return True

    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_book_analysis()
    if success:
        print("\n🎉 测试成功完成！")
    else:
        print("\n💥 测试失败！")