"""
增强版书籍分析器 - 集成智能文本分块

在原有 book_analyzer.py 的基础上，使用增强版分块器进行更智能的文本处理
"""

import re
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# 导入增强版分块器
from .enhanced_text_chunker import EnhancedTextChunker, ChunkStrategy

# 导入原始模块用于兼容
from .text_processor import TextProcessor
from .file_parser import FileParser

logger = logging.getLogger(__name__)


class BookAnalyzerV2:
    """
    增强版书籍分析器

    主要改进：
    1. 使用 EnhancedTextChunker 进行智能分块
    2. 支持多种分块策略
    3. 更好的章节检测
    4. 可选的 MinerU 集成
    """

    def __init__(
        self,
        llm_client,
        chunking_strategy: str = "hybrid",
        chunk_size: int = 1000,
        use_mineru: bool = False
    ):
        self.llm_client = llm_client

        # 创建增强版分块器
        self.chunker = EnhancedTextChunker(
            strategy=ChunkStrategy(chunking_strategy),
            chunk_size=chunk_size,
            overlap=100,
            use_mineru=use_mineru,
            enable_semantic=True
        )

        # 保留原始处理器用于兼容
        self.text_processor = TextProcessor()
        self.file_parser = FileParser()

    def analyze_book(
        self,
        file_path: str,
        options: Optional[Dict] = None
    ) -> Dict:
        """
        执行完整的四阶段拆书分析

        Args:
            file_path: 文件路径
            options: 配置选项
                - chunking_strategy: 分块策略 (chapter/semantic/fixed_size/adaptive/hybrid)
                - chunk_size: 分块大小
                - unit_size: 剧情单元包含的章节数

        Returns:
            分析结果字典
        """
        if options is None:
            options = {}

        logger.info(f"开始分析书籍: {file_path}")

        # 解析文件
        logger.info("阶段0: 文件解析")
        file_data = self._parse_file(file_path)

        # 阶段1：前置预处理 - 智能分块
        logger.info("阶段1: 智能文本分块")
        chunks = self._chunk_text(file_data, options)

        # 阶段2：顶层宏观拆书 - 核心总纲
        logger.info("阶段2: 宏观分析")
        world_outline, main_plot, character_settings = self.stage2_macro_analysis(chunks)

        # 确保character_settings是列表
        if character_settings is None:
            character_settings = []

        # 阶段3：中层中观拆书 - 单元5维分析
        logger.info("阶段3: 中观分析")
        unit_analyses = self.stage3_middle_analysis(chunks, character_settings, options)

        # 阶段4：底层微观拆书 - 单章细纲
        logger.info("阶段4: 微观分析")
        chapter_analyses = self.stage4_micro_analysis(file_data, chunks)

        # 汇总结果
        result = {
            "book_info": {
                "filename": file_data['filename'],
                "total_chapters": file_data['total_chapters'],
                "total_chunks": len(chunks),
                "chunking_strategy": options.get('chunking_strategy', 'hybrid')
            },
            "stage1_chunks": [chunk.to_dict() for chunk in chunks],
            "stage2_world_outline": world_outline,
            "stage2_main_plot": main_plot,
            "stage2_characters": character_settings,
            "stage3_units_analysis": unit_analyses,
            "stage4_chapters_analysis": chapter_analyses
        }

        logger.info("书籍分析完成")
        return result

    def _parse_file(self, file_path: str) -> Dict:
        """解析文件"""
        return self.file_parser.parse_file(file_path)

    def _chunk_text(self, file_data: Dict, options: Dict) -> List:
        """
        使用增强版分块器进行智能分块

        Returns:
            分块对象列表
        """
        # 获取配置
        strategy = options.get('chunking_strategy', 'hybrid')
        chunk_size = options.get('chunk_size', 1000)

        # 更新分块器配置
        if strategy != self.chunker.strategy.value:
            self.chunker.strategy = ChunkStrategy(strategy)

        if chunk_size != self.chunker.chunk_size:
            self.chunker.chunk_size = chunk_size

        # 执行分块
        chunks = self.chunker.chunk_text(
            file_data['content'],
            metadata={
                'filename': file_data['filename'],
                'file_size': file_data['file_size'],
                'total_chapters': file_data['total_chapters']
            }
        )

        logger.info(f"生成了 {len(chunks)} 个分块")
        return chunks

    def stage2_macro_analysis(
        self,
        chunks: List,
    ) -> tuple:
        """
        阶段2：顶层宏观拆书

        使用分块后的内容进行宏观分析
        """
        # 合并所有分块内容
        full_text = '\n'.join([chunk.content for chunk in chunks])

        # 提取章节信息（如果存在）
        chapters_info = []
        for chunk in chunks:
            if 'chapter_title' in chunk.metadata:
                chapters_info.append({
                    'title': chunk.metadata['chapter_title'],
                    'number': chunk.metadata.get('chapter_number'),
                    'start': chunk.start_pos,
                    'end': chunk.end_pos
                })

        # 构建分析提示
        prompt = self._build_macro_analysis_prompt(full_text, chapters_info)

        # 调用 LLM
        try:
            response = self.llm_client.generate(prompt)

            # 解析响应
            world_outline = self._extract_section(response, "世界观")
            main_plot = self._extract_section(response, "主线剧情")
            character_settings = self._extract_section(response, "角色设定")

            return world_outline, main_plot, character_settings

        except Exception as e:
            logger.error(f"宏观分析失败: {e}")
            return None, None, []

    def stage3_middle_analysis(
        self,
        chunks: List,
        character_settings: List,
        options: Dict
    ) -> List[Dict]:
        """
        阶段3：中层中观拆书 - 单元5维分析

        Args:
            chunks: 分块列表
            character_settings: 角色设定
            options: 配置选项

        Returns:
            单元分析列表
        """
        unit_size = options.get('unit_size', 5)

        # 将分块按章节分组（如果有章节信息）
        units = []
        current_unit = []

        for chunk in chunks:
            current_unit.append(chunk)

            # 判断是否应该结束当前单元
            should_end_unit = False

            # 如果有章节信息，按章节数分组
            if 'chapter_number' in chunk.metadata:
                chapter_num = chunk.metadata['chapter_number']
                unit_chapter_nums = [
                    c.metadata.get('chapter_number')
                    for c in current_unit
                    if 'chapter_number' in c.metadata
                ]
                if unit_chapter_nums:
                    max_chapter = max(unit_chapter_nums)
                    if max_chapter - unit_chapter_nums[0] >= unit_size - 1:
                        should_end_unit = True

            # 如果没有章节信息，按分块数量分组
            elif len(current_unit) >= unit_size:
                should_end_unit = True

            if should_end_unit:
                units.append(current_unit)
                current_unit = []

        # 添加最后一个单元
        if current_unit:
            units.append(current_unit)

        # 对每个单元进行5维分析
        unit_analyses = []

        for i, unit_chunks in enumerate(units):
            unit_content = '\n'.join([c.content for c in unit_chunks])
            unit_metadata = {
                'unit_number': i + 1,
                'chunk_count': len(unit_chunks),
                'word_count': sum(c.word_count for c in unit_chunks)
            }

            # 构建分析提示
            prompt = self._build_unit_analysis_prompt(
                unit_content,
                character_settings,
                unit_metadata
            )

            # 调用 LLM
            try:
                response = self.llm_client.generate(prompt)

                # 提取5维分析结果
                analysis = {
                    "unit_number": i + 1,
                    "unit_info": unit_metadata,
                    "剧情推进": self._extract_section(response, "剧情推进"),
                    "人物刻画": self._extract_section(response, "人物刻画"),
                    "冲突矛盾": self._extract_section(response, "冲突矛盾"),
                    "伏笔铺垫": self._extract_section(response, "伏笔铺垫"),
                    "情感节奏": self._extract_section(response, "情感节奏")
                }

                unit_analyses.append(analysis)

            except Exception as e:
                logger.error(f"单元 {i+1} 分析失败: {e}")
                unit_analyses.append({
                    "unit_number": i + 1,
                    "unit_info": unit_metadata,
                    "error": str(e)
                })

        return unit_analyses

    def stage4_micro_analysis(
        self,
        file_data: Dict,
        chunks: List
    ) -> List[Dict]:
        """
        阶段4：底层微观拆书 - 单章细纲

        Args:
            file_data: 文件数据
            chunks: 分块列表

        Returns:
            章节分析列表
        """
        chapter_analyses = []

        # 按章节分组分块
        chapters_data = {}
        for chunk in chunks:
            chapter_num = chunk.metadata.get('chapter_number')
            if chapter_num is not None:
                if chapter_num not in chapters_data:
                    chapters_data[chapter_num] = {
                        'title': chunk.metadata.get('chapter_title', f'第{chapter_num}章'),
                        'chunks': []
                    }
                chapters_data[chapter_num]['chunks'].append(chunk)

        # 对每个章节进行细纲分析
        for chapter_num, data in sorted(chapters_data.items()):
            chapter_content = '\n'.join([c.content for c in data['chunks']])

            # 构建分析提示
            prompt = self._build_chapter_analysis_prompt(
                data['title'],
                chapter_content
            )

            # 调用 LLM
            try:
                response = self.llm_client.generate(prompt)

                analysis = {
                    "chapter_number": chapter_num,
                    "chapter_title": data['title'],
                    "word_count": sum(c.word_count for c in data['chunks']),
                    "细纲": self._extract_section(response, "章节细纲"),
                    "关键情节": self._extract_section(response, "关键情节"),
                    "主要对话": self._extract_section(response, "主要对话"),
                    "场景描写": self._extract_section(response, "场景描写")
                }

                chapter_analyses.append(analysis)

            except Exception as e:
                logger.error(f"章节 {chapter_num} 分析失败: {e}")

        return chapter_analyses

    # ==================== 提示词构建方法 ====================

    def _build_macro_analysis_prompt(
        self,
        text: str,
        chapters_info: List[Dict]
    ) -> str:
        """构建宏观分析提示词"""
        chapters_summary = "\n".join([
            f"{i+1}. {ch['title']}"
            for i, ch in enumerate(chapters_info[:20])  # 限制章节数量
        ])

        prompt = f"""
请分析以下网文文本，提取核心总纲信息：

【章节目录】
{chapters_summary if chapters_summary else '（无章节信息）'}

【正文内容】
{text[:5000]}...

请按以下格式输出：

## 世界观
（描述小说的世界设定、力量体系、社会结构等）

## 主线剧情
（概括故事的主要情节发展和脉络）

## 角色设定
（列出主要角色及其核心设定，每行一个角色，格式：角色名 - 设定描述）
"""
        return prompt

    def _build_unit_analysis_prompt(
        self,
        unit_content: str,
        character_settings: List,
        unit_metadata: Dict
    ) -> str:
        """构建单元分析提示词"""
        chars_summary = "\n".join([
            f"- {char[:50]}..." for char in character_settings[:5]
        ])

        prompt = f"""
请对以下剧情单元进行5维分析：

【单元信息】
- 单元编号：{unit_metadata['unit_number']}
- 包含分块数：{unit_metadata['chunk_count']}
- 字数：{unit_metadata['word_count']}

【角色背景】
{chars_summary if character_settings else '（无角色信息）'}

【单元内容】
{unit_content[:3000]}...

请从以下5个维度进行分析：

## 剧情推进
（描述本单元剧情如何推进，发生了什么主要事件）

## 人物刻画
（分析本单元中重要人物的表现、成长或变化）

## 冲突矛盾
（识别本单元中的主要冲突和矛盾点）

## 伏笔铺垫
（指出为后续情节埋下的伏笔）

## 情感节奏
（描述读者情感的变化节奏，如紧张、舒缓、感动等）
"""
        return prompt

    def _build_chapter_analysis_prompt(
        self,
        chapter_title: str,
        chapter_content: str
    ) -> str:
        """构建章节细纲分析提示词"""
        prompt = f"""
请为以下章节生成详细细纲：

【章节标题】
{chapter_title}

【章节内容】
{chapter_content[:4000]}...

请按以下格式输出：

## 章节细纲
（详细的章节情节分解，按时间顺序）

## 关键情节
（列出本章的关键情节点，每行一个）

## 主要对话
（提取本章的重要对话片段，标注对话角色）

## 场景描写
（描述本章的重要场景和环境描写）
"""
        return prompt

    # ==================== 辅助方法 ====================

    def _extract_section(self, text: str, section_name: str) -> str:
        """从LLM响应中提取特定章节内容"""
        pattern = rf'##\s*{re.escape(section_name)}\s*\n(.*?)(?=##\s*|$)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""


# 便捷函数
def analyze_book_file(
    file_path: str,
    llm_client,
    chunking_strategy: str = "hybrid",
    chunk_size: int = 1000,
    use_mineru: bool = False,
    **options
) -> Dict:
    """
    便捷函数：分析书籍文件

    Args:
        file_path: 文件路径
        llm_client: LLM客户端
        chunking_strategy: 分块策略
        chunk_size: 分块大小
        use_mineru: 是否使用MinerU
        **options: 其他配置选项

    Returns:
        分析结果字典
    """
    analyzer = BookAnalyzerV2(
        llm_client=llm_client,
        chunking_strategy=chunking_strategy,
        chunk_size=chunk_size,
        use_mineru=use_mineru
    )

    return analyzer.analyze_book(file_path, options)
