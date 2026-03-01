"""
增强仿写引擎 - 基于拆书结果的深度创作
"""

import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

from .novel_adaptation_engine import NovelAdaptationEngine

logger = logging.getLogger(__name__)


class EnhancedAdaptationEngine(NovelAdaptationEngine):
    """
    增强仿写引擎

    改进：
    1. 直接基于拆书结果进行创作
    2. 深度利用世界观、角色、剧情结构
    3. 支持多种创作模式
    4. 提供创作质量控制
    """

    def __init__(self, llm_client, **kwargs):
        super().__init__(llm_client, **kwargs)
        self.analysis_data = None
        self.creation_modes = {
            'faithful': '忠实仿写 - 保持原结构和风格',
            'creative': '创意改写 - 保留核心但自由创作',
            'parallel': '平行世界 - 相似世界观但新故事',
            'prequel': '前传故事 - 原作的背景故事',
            'sequel': '续集故事 - 原作之后的故事'
        }

    def load_analysis_result(self, analysis_path: str):
        """加载拆书结果"""
        try:
            with open(analysis_path, 'r', encoding='utf-8') as f:
                self.analysis_data = json.load(f)
            logger.info(f"成功加载拆书结果: {analysis_path}")
        except Exception as e:
            logger.error(f"加载拆书结果失败: {str(e)}")
            raise

    def generate_adaptation(self, config: Dict) -> Dict:
        """基于拆书结果生成仿写内容"""
        if not self.analysis_data:
            raise ValueError("请先加载拆书结果")

        # 提取关键信息
        world_outline = self.analysis_data.get('stage2_world_outline', {})
        main_plot = self.analysis_data.get('stage2_main_plot', {})
        characters = self.analysis_data.get('stage2_characters', [])
        units = self.analysis_data.get('stage1_units', [])

        # 构建仿写提示
        adaptation_prompt = self._build_adaptation_prompt(
            config,
            world_outline,
            main_plot,
            characters,
            units
        )

        # 生成仿写内容
        adapted_content = self._generate_adapted_content(adaptation_prompt, config)

        # 构建结果
        result = {
            'config': config,
            'metadata': {
                'creation_mode': config.get('mode', 'faithful'),
                'target_chapters': config.get('target_chapters', 10),
                'target_words': config.get('target_words', 50000),
                'created_at': datetime.now().isoformat()
            },
            'adapted_content': adapted_content,
            'world_inspired': self._extract_world_inspiration(world_outline),
            'character_inspired': self._extract_character_inspiration(characters),
            'plot_inspired': self._extract_plot_inspiration(main_plot),
            'quality_metrics': self._assess_quality(adapted_content)
        }

        return result

    def _build_adaptation_prompt(
        self,
        config: Dict,
        world_outline: Dict,
        main_plot: Dict,
        characters: List,
        units: List
    ) -> str:
        """构建仿写提示词"""

        # 创作模式说明
        mode_descriptions = {
            'faithful': '保持原作的世界观、角色设定和剧情结构，只改变表达方式和细节',
            'creative': '保留世界观和核心角色，但创作新的剧情故事',
            'parallel': '在相似的世界观中，创作全新的故事和角色',
            'prequel': '创作原作之前的故事，解释世界观和角色的背景',
            'sequel': '创作原作之后的故事，延续世界观和发展角色'
        }

        prompt = f"""
【仿写任务说明】
创作模式: {config.get('mode', 'faithful')}
{mode_descriptions.get(config.get('mode', 'faithful'), '')}

【原始世界观参考】
"""

        # 添加世界观信息
        if world_outline:
            prompt += f"""
世界观背景:
- 时空背景: {world_outline.get('基础时空背景', '未知')}
- 核心力量体系: {json.dumps(world_outline.get('核心力量体系', {}), ensure_ascii=False)}
- 核心势力: {json.dumps(world_outline.get('核心势力划分', []), ensure_ascii=False)}
- 世界规则: {world_outline.get('世界核心规则/铁则', '未知')}

"""

        # 添加角色信息
        if characters:
            prompt += "【主要角色设定】\n"
            for char in characters[:5]:  # 限制数量避免过长
                if isinstance(char, dict) and 'name' in char:
                    prompt += f"- {char.get('name', '未知')}: {char.get('description', '未知')}\n"
            prompt += "\n"

        # 添加剧情结构
        if main_plot:
            plot_info = main_plot.get('核心大纲', {})
            if '一句话完整概括' in plot_info:
                prompt += f"【剧情概览】\n{plot_info['一句话完整概括']}\n\n"
            if '全书核心剧情节点' in plot_info:
                prompt += "【剧情结构】\n"
                for key, value in plot_info['全书核心剧情节点'].items():
                    prompt += f"- {key}: {value}\n"
                prompt += "\n"

        # 添加剧情单元
        if units:
            prompt += f"【剧情单元模板】（共{len(units)}个单元）\n"
            for unit in units[:3]:  # 展示前3个作为示例
                prompt += f"""
单元{unit.get('unit_number', 0)}:
- 主题: {unit.get('theme', '未知')}
- 内容预览: {unit.get('content', '')[:200]}...
- 关键词: {', '.join(unit.get('keywords', []))}
"""

        # 添加创作要求
        prompt += f"""
【创作要求】
1. 基于以上拆书结果进行创作
2. 目标章节数: {config.get('target_chapters', 10)}
3. 目标总字数: {config.get('target_words', 50000)}
4. 仿写风格: {config.get('style', '保持原风格')}
5. 原创度: {config.get('originality', '中等')}%
6. 写作要求:
   - 保持叙事流畅性
   - 确保角色一致性
   - 遵循世界观设定
   - 创作引人入胜的情节

请开始创作:
"""

        return prompt

    def _generate_adapted_content(self, prompt: str, config: Dict) -> List[Dict]:
        """生成仿写内容"""
        # 使用LLM进行批量创作
        adapted_chapters = []

        # 根据目标章节数进行分批创作
        target_chapters = config.get('target_chapters', 10)
        batch_size = 3  # 每批生成3章

        for i in range(0, target_chapters, batch_size):
            batch_end = min(i + batch_size, target_chapters)
            batch_prompt = f"""
【创作批次 {i//batch_size + 1}】
请创作第 {i+1} 到第 {batch_end} 章。

{prompt}
"""

            # 调用LLM生成内容
            response = self.llm_client.generate(
                prompt=batch_prompt,
                system_prompt="你是一位专业的小说作家，善于创作引人入胜的故事。",
                max_tokens=4000,
                temperature=0.8
            )

            # 解析生成的章节内容
            chapters = self._parse_chapter_response(response, i+1, batch_end)
            adapted_chapters.extend(chapters)

        return adapted_chapters

    def _parse_chapter_response(self, response: str, start_num: int, end_num: int) -> List[Dict]:
        """解析LLM返回的章节内容"""
        # 这里需要实现章节内容的解析逻辑
        # 可以基于特定的格式进行解析

        chapters = []
        lines = response.split('\n')

        current_chapter = None
        current_content = []

        for line in lines:
            # 检测章节标题
            if line.startswith('第') and '章' in line:
                # 保存上一章
                if current_chapter:
                    chapters.append({
                        'chapter_number': current_chapter['number'],
                        'title': current_chapter['title'],
                        'content': '\n'.join(current_content).strip(),
                        'word_count': len(''.join(current_content))
                    })

                # 开始新章
                chapter_num = int(line.split('第')[1].split('章')[0])
                if chapter_num >= start_num and chapter_num <= end_num:
                    current_chapter = {
                        'number': chapter_num,
                        'title': line.strip()
                    }
                    current_content = []

            elif current_chapter:
                current_content.append(line)

        # 保存最后一章
        if current_chapter:
            chapters.append({
                'chapter_number': current_chapter['number'],
                'title': current_chapter['title'],
                'content': '\n'.join(current_content).strip(),
                'word_count': len(''.join(current_content))
            })

        return chapters

    def _extract_world_inspiration(self, world_outline: Dict) -> Dict:
        """提取世界观启发点"""
        return {
            'core_concepts': world_outline.get('核心力量体系', {}).get('阶段划分', []),
            'key_settings': world_outline.get('核心差异化设定', ''),
            'rules': world_outline.get('世界核心规则/铁则', '')
        }

    def _extract_character_inspiration(self, characters: List) -> List[Dict]:
        """提取角色启发点"""
        return [
            {
                'name': char.get('name', ''),
                'type': char.get('type', ''),
                'personality': char.get('personality', ''),
                'key_traits': char.get('key_traits', [])
            }
            for char in characters[:10]  # 限制数量
        ]

    def _extract_plot_inspiration(self, main_plot: Dict) -> Dict:
        """提取剧情启发点"""
        plot_info = main_plot.get('核心大纲', {})
        return {
            'core_summary': plot_info.get('一句话完整概括', ''),
            'key_events': plot_info.get('全书核心剧情节点', {})
        }

    def _assess_quality(self, content: List[Dict]) -> Dict:
        """评估创作质量"""
        total_words = sum(chapter.get('word_count', 0) for chapter in content)

        return {
            'total_chapters': len(content),
            'total_words': total_words,
            'average_words_per_chapter': total_words / len(content) if content else 0,
            'completeness': '完成' if len(content) > 0 else '未开始',
            'timestamp': datetime.now().isoformat()
        }