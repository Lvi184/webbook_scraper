#!/usr/bin/env python
"""
仿写测试模块 - 用于测试小说仿写功能

功能：
1. 加载已有的拆书分析结果
2. 配置仿写参数
3. 执行仿写
4. 展示结果
"""

import json
import os
from pathlib import Path
from services.llm_client import LLMClient
from services.novel_adaptation_engine import NovelAdaptationEngine

def load_analysis_result(analysis_path: str) -> dict:
    """加载拆书分析结果"""
    try:
        with open(analysis_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载拆书结果失败: {str(e)}")
        return None

def create_adaptation_config() -> dict:
    """创建仿写配置"""
    return {
        'mode': 'parallel',  # 平行世界模式
        'target_chapters': 3,  # 目标章节数
        'target_words': 3000,  # 目标总字数
        'style': '重生魔法时间性',  # 仿写风格
        'originality': 50,  # 原创度
        'world_view': {
            '背景': '魔法世界',
            '时间线': '现代重生'
        },
        'characters': {
            '主角': '年轻魔法师',
            '反派': '黑暗巫师'
        },
        'plot': {
            '核心冲突': '魔法力量争夺',
            '结局': '正义胜利'
        }
    }

def test_adaptation():
    """测试仿写功能"""
    print("🚀 开始仿写测试...")
    
    # 1. 输入API密钥
    api_key = "sk-cd50e38e3208480f9b892e2a861e908c"
    
    # 2. 选择模型
    provider = "openai"
    model = "qwen-turbo"
    
    # 3. 初始化LLM客户端
    print("初始化LLM客户端...")
    llm_client = LLMClient(api_key, provider, model)
    
    # 4. 初始化仿写引擎
    adaptation_engine = NovelAdaptationEngine(llm_client)
    
    # 5. 选择拆书分析结果
    analysis_dir = Path("data/analysis")
    if not analysis_dir.exists():
        print("❌ 拆书分析结果目录不存在，请先执行拆书分析")
        return
    
    # 列出可用的分析结果
    analysis_files = list(analysis_dir.glob("*.json"))
    if not analysis_files:
        print("❌ 没有找到拆书分析结果，请先执行拆书分析")
        return
    
    print("\n可用的拆书分析结果:")
    for i, file in enumerate(analysis_files):
        print(f"{i+1}. {file.name}")
    
    # 选择分析结果
    choice = int(input("请选择要使用的拆书分析结果编号: ")) - 1
    if choice < 0 or choice >= len(analysis_files):
        print("❌ 无效的选择")
        return
    
    analysis_path = analysis_files[choice]
    print(f"\n使用拆书分析结果: {analysis_path.name}")
    
    # 6. 加载拆书分析结果
    adaptation_engine.load_analysis_result(str(analysis_path))
    
    # 7. 创建仿写配置
    config = create_adaptation_config()
    print("\n仿写配置:")
    print(json.dumps(config, ensure_ascii=False, indent=2))
    
    # 8. 执行仿写
    print("\n开始执行仿写...")
    try:
        result = adaptation_engine.generate_adaptation(config)
        print("✅ 仿写完成！")
        
        # 9. 展示结果
        print("\n仿写结果:")
        print(f"配置: {json.dumps(result['config'], ensure_ascii=False, indent=2)}")
        print(f"元数据: {json.dumps(result['metadata'], ensure_ascii=False, indent=2)}")
        
        # 展示章节
        chapters = result.get('adapted_content', [])
        print(f"\n生成章节数: {len(chapters)}")
        for i, chapter in enumerate(chapters):
            print(f"\n第{i+1}章: {chapter.get('title', f'第{i+1}章')}")
            print(f"字数: {chapter.get('word_count', 0)}")
            print(f"内容: {chapter.get('content', '')[:200]}...")
        
        # 10. 保存结果
        output_dir = Path("data/test_results")
        output_dir.mkdir(exist_ok=True, parents=True)
        
        output_file = output_dir / f"adaptation_test_{Path(analysis_path).stem}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 仿写结果已保存到: {output_file}")
        
    except Exception as e:
        print(f"❌ 仿写失败: {str(e)}")

if __name__ == "__main__":
    test_adaptation()
