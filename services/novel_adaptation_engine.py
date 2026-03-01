"""
小说仿写引擎 - 基于拆书逻辑的自动化仿写系统

核心功能：
1. 读取原始拆书结果
2. 应用用户设定的改编方向
3. 自动生成仿写内容
4. 控制仿写章节数量和字数
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path
from .enhanced_text_chunker import EnhancedTextChunker, ChunkStrategy
from .optimized_book_analyzer import OptimizedBookAnalyzer

logger = logging.getLogger(__name__)


class NovelAdaptationEngine:
    """
    小说仿写引擎

    特性：
    - 基于拆书逻辑的自动化仿写
    - 支持用户自定义改编方向
    - 控制仿写章节数量和字数
    - 保持原作结构和节奏
    - 自动提取对应内容进行仿写
    """

    def __init__(
        self,
        llm_client,
        chunking_strategy: str = "hybrid",
        chunk_size: int = 1000,
        use_mineru: bool = False
    ):
        self.llm_client = llm_client
        self.chunker = EnhancedTextChunker(
            strategy=ChunkStrategy(chunking_strategy),
            chunk_size=chunk_size,
            overlap=100,
            use_mineru=use_mineru,
            enable_semantic=True
        )
        self.analyzer = OptimizedBookAnalyzer(
            llm_client=llm_client,
            chunking_strategy=chunking_strategy,
            chunk_size=chunk_size,
            use_mineru=use_mineru
        )

    def adapt_novel(
        self,
        original_book_path: str,
        adaptation_config: Dict,
        output_path: str = None,
        chapters_to_adapt: int = 3,
        target_word_count: Optional[int] = None
    ) -> Dict:
        """
        执行完整的小说仿写流程

        Args:
            original_book_path: 原始书籍路径
            adaptation_config: 改编配置
            output_path: 输出路径（可选）
            chapters_to_adapt: 要仿写的章节数量
            target_word_count: 目标字数（可选）

        Returns:
            仿写结果字典
        """
        logger.info("开始小说仿写流程")

        # 1. 拆解原始书籍
        logger.info("步骤1: 拆解原始书籍")
        original_analysis = self.analyzer.analyze_book(original_book_path, adaptation_config)

        # 2. 应用改编配置
        logger.info("步骤2: 应用改编配置")
        # 从配置中获取目标章节数
        target_chapters = adaptation_config.get('target_chapters', chapters_to_adapt)
        adapted_content = self._apply_adaptation_config(
            original_analysis,
            adaptation_config,
            target_chapters,
            target_word_count
        )

        # 3. 生成仿写内容
        logger.info("步骤3: 生成仿写内容")
        adapted_novel = self._generate_adapted_content(
            original_analysis,
            adapted_content,
            adaptation_config
        )

        # 4. 保存结果
        if output_path:
            logger.info(f"步骤4: 保存仿写结果到 {output_path}")
            self._save_adapted_novel(adapted_novel, output_path)

        logger.info("小说仿写完成")
        return adapted_novel

    def _apply_adaptation_config(
        self,
        original_analysis: Dict,
        config: Dict,
        chapters_to_adapt: int,
        target_word_count: Optional[int]
    ) -> Dict:
        """
        应用改编配置到原始拆解结果

        Args:
            original_analysis: 原始拆解结果
            config: 改编配置
            chapters_to_adapt: 要仿写的章节数量
            target_word_count: 目标字数

        Returns:
            适配后的内容配置
        """
        # 提取改编配置
        world_view_config = config.get('world_view', {})
        character_config = config.get('characters', {})
        plot_config = config.get('plot', {})
        style_config = config.get('style', {})

        # 获取原始拆解结果
        units = original_analysis['stage1_units']
        unit_analyses = original_analysis['stage3_units_analysis']
        chapter_analyses = original_analysis['stage4_chapters_analysis']

        # 限制要仿写的章节数量，确保不超出实际章节数
        actual_chapters = len(chapter_analyses)
        actual_units = len(units)
        
        # 确保不超过实际章节数
        chapters_to_adapt = min(chapters_to_adapt, actual_chapters, actual_units)
        
        # 限制要仿写的章节数量
        adapted_units = units[:chapters_to_adapt]
        adapted_unit_analyses = unit_analyses[:chapters_to_adapt]
        adapted_chapter_analyses = chapter_analyses[:chapters_to_adapt]

        # 应用改编配置
        adapted_content = {
            'world_view': {
                'original': self._extract_world_view(original_analysis),
                'adapted': world_view_config
            },
            'characters': {
                'original': self._extract_characters(original_analysis),
                'adapted': character_config
            },
            'plot': {
                'original': self._extract_plot(original_analysis),
                'adapted': plot_config
            },
            'style': {
                'original': self._extract_style(original_analysis),
                'adapted': style_config
            },
            'units': adapted_units,
            'unit_analyses': adapted_unit_analyses,
            'chapter_analyses': adapted_chapter_analyses,
            'chapters_to_adapt': chapters_to_adapt,
            'target_word_count': target_word_count
        }

        return adapted_content

    def _extract_world_view(self, analysis: Dict) -> Dict:
        """从拆解结果中提取世界观信息"""
        return {
            'world_outline': analysis['stage2_world_outline'],
            'unit_world_view': [ua['单元世界观设计'] for ua in analysis['stage3_units_analysis']],
            'chapter_world_view': [ca['本章核心创作逻辑拆解'] for ca in analysis['stage4_chapters_analysis']]
        }

    def _extract_characters(self, analysis: Dict) -> Dict:
        """从拆解结果中提取角色信息"""
        return {
            'character_settings': analysis['stage2_characters'],
            'unit_character_design': [ua['单元人物塑造设计'] for ua in analysis['stage3_units_analysis']],
            'chapter_character_design': [ca['本章核心创作逻辑拆解'] for ca in analysis['stage4_chapters_analysis']]
        }

    def _extract_plot(self, analysis: Dict) -> Dict:
        """从拆解结果中提取剧情信息"""
        return {
            'main_outline': analysis['stage2_main_outline'],
            'unit_outline': [ua['单元大纲设计'] for ua in analysis['stage3_units_analysis']],
            'chapter_outline': [ca['本章剧情细纲'] for ca in analysis['stage4_chapters_analysis']]
        }

    def _extract_style(self, analysis: Dict) -> Dict:
        """从拆解结果中提取文风信息"""
        return {
            'writing_style': "古龙式经典武侠文风。语言精炼，富有诗意和哲理，惜字如金。注重环境描写和氛围烘托，以景衬人。对话极简，但张力十足，完全服务于人物塑造和情节推进。叙事节奏独特，缓时极缓，快时极快，形成强烈的阅读冲击力。",
            'unit_style': [ua['单元情绪设计'] for ua in analysis['stage3_units_analysis']],
            'chapter_style': [ca['本章核心创作逻辑拆解'] for ca in analysis['stage4_chapters_analysis']]
        }

    def _generate_adapted_content(
        self,
        original_analysis: Dict,
        adapted_content: Dict,
        config: Dict
    ) -> Dict:
        """
        生成仿写内容

        Args:
            original_analysis: 原始拆解结果
            adapted_content: 适配后的内容配置
            config: 改编配置

        Returns:
            仿写结果
        """
        adapted_novel = {
            'adaptation_config': config,
            'original_analysis': original_analysis,
            'adapted_content': adapted_content,
            'chapters': []
        }

        # 获取要仿写的章节
        chapters_to_adapt = adapted_content['chapters_to_adapt']
        chapter_analyses = adapted_content['chapter_analyses']

        for i in range(chapters_to_adapt):
            if i < len(chapter_analyses):
                chapter_analysis = chapter_analyses[i]
                # 确保 chapter_number 存在
                chapter_number = chapter_analysis.get('chapter_number', i + 1)
                chapter_title = chapter_analysis.get('chapter_title', chapter_analysis.get('title', f"第{chapter_number}章"))

                # 生成仿写章节
                adapted_chapter = self._generate_adapted_chapter(
                    chapter_analysis,
                    adapted_content,
                    i
                )

                adapted_novel['chapters'].append({
                    'chapter_number': chapter_number,
                    'chapter_title': chapter_title,
                    'adapted_content': adapted_chapter,
                    'original_analysis': chapter_analysis
                })

        return adapted_novel

    def _generate_adapted_chapter(
        self,
        chapter_analysis: Dict,
        adapted_content: Dict,
        chapter_index: int
    ) -> str:
        """
        生成仿写章节内容

        Args:
            chapter_analysis: 章节分析结果
            adapted_content: 适配后的内容配置
            chapter_index: 章节索引

        Returns:
            仿写章节内容
        """
        # 构建仿写提示
        prompt = self._build_adaptation_prompt(
            chapter_analysis,
            adapted_content,
            chapter_index
        )

        # 调用LLM生成内容
        try:
            adapted_content = self.llm_client.generate(prompt)
            return adapted_content.strip()
        except Exception as e:
            logger.error(f"章节 {chapter_index + 1} 仿写失败: {e}")
            return f"仿写失败: {str(e)}"

    def _build_adaptation_prompt(
        self,
        chapter_analysis: Dict,
        adapted_content: Dict,
        chapter_index: int
    ) -> str:
        """
        构建仿写提示词

        Args:
            chapter_analysis: 章节分析结果
            adapted_content: 适配后的内容配置
            chapter_index: 章节索引

        Returns:
            仿写提示词
        """
        # 获取改编配置
        world_view_config = adapted_content['world_view']['adapted']
        character_config = adapted_content['characters']['adapted']
        plot_config = adapted_content['plot']['adapted']
        style_config = adapted_content['style']['adapted']

        # 获取原始章节信息
        chapter_number = chapter_analysis['chapter_number']
        chapter_title = chapter_analysis.get('chapter_title', chapter_analysis.get('title', f"第{chapter_number}章"))
        original_outline = chapter_analysis.get('本章剧情细纲', chapter_analysis.get('剧情细纲', ''))
        original_style = chapter_analysis.get('本章核心创作逻辑拆解', chapter_analysis.get('核心创作逻辑', ''))

        # 构建提示
        prompt = f"""
请基于以下信息进行小说仿写：

【仿写配置】
- 世界观：{world_view_config}
- 角色：{character_config}
- 剧情：{plot_config}
- 文风：{style_config}

【原始章节信息】
- 章节编号：第{chapter_number}章
- 章节标题：{chapter_title}
- 原始剧情细纲：
{original_outline}
- 原始创作逻辑：
{original_style}

【仿写要求】
1. 保持原作的结构和节奏，但替换世界观、角色设定
2. 保留原作的核心情节节点和爽点设计
3. 适配新的设定要求，确保人设和世界观的一致性
4. 保持目标字数：{adapted_content['target_word_count']}字（如果指定）
5. 生成完整的章节内容，包括环境描写、人物对话、情节推进

请生成仿写后的第{chapter_number}章内容：
"""

        return prompt

    def _save_adapted_novel(self, adapted_novel: Dict, output_path: str) -> None:
        """
        保存仿写结果

        Args:
            adapted_novel: 仿写结果
            output_path: 输出路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(adapted_novel, f, ensure_ascii=False, indent=2)

    def create_adaptation_config(self, user_requirements: Dict) -> Dict:
        """
        创建改编配置

        Args:
            user_requirements: 用户需求

        Returns:
            改编配置
        """
        return {
            'world_view': user_requirements.get('world_view', {}),
            'characters': user_requirements.get('characters', {}),
            'plot': user_requirements.get('plot', {}),
            'style': user_requirements.get('style', {}),
            'chapters_to_adapt': user_requirements.get('chapters_to_adapt', 3),
            'target_word_count': user_requirements.get('target_word_count', 2000)
        }

    def load_analysis_result(self, analysis_path: str):
        """加载拆书结果"""
        import json
        try:
            with open(analysis_path, 'r', encoding='utf-8') as f:
                self.analysis_data = json.load(f)
        except Exception as e:
            logger.error(f"加载拆书结果失败: {str(e)}")
            raise

    def generate_adaptation(self, config: Dict) -> Dict:
        """基于拆书结果生成仿写内容"""
        if not self.analysis_data:
            raise ValueError("请先加载拆书结果")

        # 创建增强仿写引擎实例
        from .enhanced_adaptation_engine import EnhancedAdaptationEngine
        enhanced_engine = EnhancedAdaptationEngine(self.llm_client)
        enhanced_engine.analysis_data = self.analysis_data

        return enhanced_engine.generate_adaptation(config)


# 便捷函数
def create_adaptation_config(
    world_view: Dict,
    characters: Dict,
    plot: Dict,
    style: Dict,
    chapters_to_adapt: int = 3,
    target_word_count: int = 2000
) -> Dict:
    """
    创建改编配置的便捷函数

    Args:
        world_view: 世界观配置
        characters: 角色配置
        plot: 剧情配置
        style: 文风配置
        chapters_to_adapt: 要仿写的章节数量
        target_word_count: 目标字数

    Returns:
        改编配置
    """
    return {
        'world_view': world_view,
        'characters': characters,
        'plot': plot,
        'style': style,
        'chapters_to_adapt': chapters_to_adapt,
        'target_word_count': target_word_count
    }


def adapt_novel(
    original_book_path: str,
    adaptation_config: Dict,
    llm_client,
    output_path: str = None,
    chunking_strategy: str = "hybrid",
    chunk_size: int = 1000,
    use_mineru: bool = False
) -> Dict:
    """
    便捷函数：执行小说仿写

    Args:
        original_book_path: 原始书籍路径
        adaptation_config: 改编配置
        llm_client: LLM客户端
        output_path: 输出路径（可选）
        chunking_strategy: 分块策略
        chunk_size: 分块大小
        use_mineru: 是否使用MinerU

    Returns:
        仿写结果字典
    """
    engine = NovelAdaptationEngine(
        llm_client=llm_client,
        chunking_strategy=chunking_strategy,
        chunk_size=chunk_size,
        use_mineru=use_mineru
    )

    return engine.adapt_novel(
        original_book_path,
        adaptation_config,
        output_path
    )