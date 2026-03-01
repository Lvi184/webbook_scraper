"""
优化版书籍分析器 - 基于全维度结构化拆书方案

完全复刻参考平台的成熟拆书架构，补全适配二次改编的单章细纲模块
形成「顶层总纲→中层单元拆解→底层单章细节」的完整拆书闭环
"""

import logging
import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from .enhanced_text_chunker import EnhancedTextChunker, ChunkStrategy

logger = logging.getLogger(__name__)


class OptimizedBookAnalyzer:
    """
    优化版书籍分析器 - 基于全维度结构化拆书方案

    核心特点：
    1. 严格遵循「先全局总纲→再分单元拆解→最后单章细纲」的顺序
    2. 所有拆解内容按固定模块分类，可单独提取、替换、复用
    3. 100%原文贴合，不主观编造、不过度解读
    4. 拆解下沉到单章的每一个情节节点、情绪节点、人设节点
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

    def analyze_book(
        self,
        file_path: str,
        options: Optional[Dict] = None
    ) -> Dict:
        """
        执行完整的4阶段拆书分析

        Args:
            file_path: 文件路径
            options: 配置选项

        Returns:
            分析结果字典
        """
        if options is None:
            options = {}

        logger.info("开始全维度结构化拆书分析")

        # 阶段1：前置预处理 - 全书剧情单元划分
        logger.info("阶段1: 前置预处理 - 全书剧情单元划分")
        file_data = self._preprocess_book(file_path, options)

        # 阶段2：顶层宏观拆书 - 全书核心总纲拆解
        logger.info("阶段2: 顶层宏观拆书 - 全书核心总纲拆解")
        world_outline, main_outline, character_settings = self._macro_analysis(file_data)

        # 阶段3：中层中观拆书 - 分剧情单元5维拆解
        logger.info("阶段3: 中层中观拆书 - 分剧情单元5维拆解")
        unit_analyses = self._middle_analysis(file_data, character_settings, options)

        # 阶段4：底层微观拆书 - 单章细纲全维度拆解
        logger.info("阶段4: 底层微观拆书 - 单章细纲全维度拆解")
        chapter_analyses = self._micro_analysis(file_data)

        # 汇总结果
        result = {
            "book_info": {
                "filename": file_data['filename'],
                "total_chapters": file_data['total_chapters'],
                "total_units": len(file_data['units']),
                "chunking_strategy": options.get('chunking_strategy', 'hybrid')
            },
            "stage1_units": file_data['units'],
            "stage2_world_outline": world_outline,
            "stage2_main_outline": main_outline,
            "stage2_characters": character_settings,
            "stage3_units_analysis": unit_analyses,
            "stage4_chapters_analysis": chapter_analyses
        }

        logger.info("全维度结构化拆书分析完成")
        return result

    def _preprocess_book(self, file_path: str, options: Dict) -> Dict:
        """
        阶段1：前置预处理 - 全书剧情单元划分

        Args:
            file_path: 文件路径
            options: 配置选项

        Returns:
            包含单元划分的文件数据
        """
        # 解析文件
        file_data = self._parse_file(file_path)

        # 智能分块
        chunks = self.chunker.chunk_text(
            file_data['content'],
            metadata={'filename': file_data['filename']}
        )

        # 按章节分组（如果有章节信息）
        chapters = self._group_by_chapters(chunks)

        # 剧情单元划分
        unit_size = options.get('unit_size', 5)  # 默认每5章为1个单元
        units = self._create_units(chapters, unit_size)

        return {
            **file_data,
            'chunks': chunks,
            'chapters': chapters,
            'units': units
        }

    def _group_by_chapters(self, chunks: List) -> List[Dict]:
        """按章节分组"""
        chapters = []
        current_chapter = None

        for chunk in chunks:
            if 'chapter_number' in chunk.metadata:
                if current_chapter:
                    chapters.append(current_chapter)

                current_chapter = {
                    'chapter_number': chunk.metadata['chapter_number'],
                    'title': chunk.metadata.get('chapter_title', f'第{chunk.metadata["chapter_number"]}章'),
                    'chunks': [chunk],
                    'content': chunk.content,
                    'start_pos': chunk.start_pos,
                    'end_pos': chunk.end_pos
                }
            elif current_chapter:
                current_chapter['chunks'].append(chunk)
                current_chapter['content'] += '\n' + chunk.content
                current_chapter['end_pos'] = chunk.end_pos

        if current_chapter:
            chapters.append(current_chapter)

        return chapters

    def _create_units(self, chapters: List[Dict], unit_size: int) -> List[Dict]:
        """创建剧情单元"""
        units = []
        current_unit = []
        unit_number = 1

        for i, chapter in enumerate(chapters):
            current_unit.append(chapter)

            # 判断是否应该结束当前单元
            if (i + 1) % unit_size == 0 or i == len(chapters) - 1:
                # 计算单元核心主题
                unit_theme = self._calculate_unit_theme(current_unit)

                units.append({
                    'unit_number': unit_number,
                    'chapter_range': f"第{current_unit[0]['chapter_number']}-{current_unit[-1]['chapter_number']}章",
                    'theme': unit_theme,
                    'chapters': current_unit.copy(),
                    'content': '\n'.join([c['content'] for c in current_unit]),
                    'word_count': sum(c['word_count'] for c in current_unit)
                })

                current_unit = []
                unit_number += 1

        return units

    def _calculate_unit_theme(self, chapters: List[Dict]) -> str:
        """计算单元核心主题"""
        # 这里可以调用LLM来分析单元主题
        # 简化版：基于章节标题和内容生成主题
        chapter_titles = [c['title'] for c in chapters]
        content_preview = '\n'.join([c['content'][:200] for c in chapters])

        prompt = f"""
分析以下章节的核心主题：

章节标题：{', '.join(chapter_titles)}

内容预览：
{content_preview}

请用一句话概括这些章节的核心剧情、核心冲突、在全书中的作用。
"""

        try:
            response = self.llm_client.generate(prompt)
            return response.strip()
        except Exception as e:
            logger.warning(f"单元主题分析失败: {e}")
            return f"单元{chapters[0]['chapter_number']}-{chapters[-1]['chapter_number']}核心剧情"

    def _macro_analysis(self, file_data: Dict) -> tuple:
        """
        阶段2：顶层宏观拆书 - 全书核心总纲拆解

        Returns:
            (world_outline, main_outline, character_settings)
        """
        full_text = '\n'.join([chunk.content for chunk in file_data['chunks']])

        # 构建分析提示
        prompt = self._build_macro_analysis_prompt(full_text, file_data['units'])

        # 调用 LLM
        try:
            response = self.llm_client.generate(prompt)

            # 解析响应
            world_outline = self._extract_section(response, "世界观核心总纲")
            main_outline = self._extract_section(response, "全本核心大纲")
            character_settings = self._extract_section(response, "全本核心角色总设定")

            return world_outline, main_outline, character_settings

        except Exception as e:
            logger.error(f"宏观分析失败: {e}")
            return None, None, []

    def _build_macro_analysis_prompt(self, text: str, units: List[Dict]) -> str:
        """构建宏观分析提示词"""
        units_summary = "\n".join([
            f"{unit['unit_number']}. {unit['chapter_range']}: {unit['theme']}"
            for unit in units[:10]  # 限制单元数量
        ])

        prompt = f"""
请分析以下网文文本，提取核心总纲信息：

【单元划分】
{units_summary if units_summary else '（无单元信息）'}

【正文内容】
{text[:5000]}...

请按以下格式输出：

## 世界观核心总纲
（描述小说的世界设定、力量体系、核心设定）

## 全本核心大纲
（概括故事的主要情节发展和脉络）

## 全本核心角色总设定
（列出主要角色及其核心设定，每行一个角色，格式：角色名 - 设定描述）
"""
        return prompt

    def _middle_analysis(
        self,
        file_data: Dict,
        character_settings: List,
        options: Dict
    ) -> List[Dict]:
        """
        阶段3：中层中观拆书 - 分剧情单元5维拆解

        Args:
            file_data: 文件数据
            character_settings: 角色设定
            options: 配置选项

        Returns:
            单元分析列表
        """
        units = file_data['units']

        unit_analyses = []

        for i, unit in enumerate(units):
            unit_content = unit['content']

            # 构建分析提示
            prompt = self._build_unit_analysis_prompt(
                unit_content,
                character_settings,
                unit
            )

            # 调用 LLM
            try:
                response = self.llm_client.generate(prompt)

                # 提取5维分析结果
                analysis = {
                    "unit_number": i + 1,
                    "unit_info": {
                        "chapter_range": unit['chapter_range'],
                        "theme": unit['theme'],
                        "word_count": unit['word_count']
                    },
                    "单元大纲设计": self._extract_section(response, "单元大纲设计"),
                    "单元世界观设计": self._extract_section(response, "单元世界观设计"),
                    "单元人物塑造设计": self._extract_section(response, "单元人物塑造设计"),
                    "单元情绪设计": self._extract_section(response, "单元情绪设计"),
                    "单元角色设计校验": self._extract_section(response, "单元角色设计校验")
                }

                unit_analyses.append(analysis)

            except Exception as e:
                logger.error(f"单元 {i+1} 分析失败: {e}")
                unit_analyses.append({
                    "unit_number": i + 1,
                    "unit_info": {
                        "chapter_range": unit['chapter_range'],
                        "theme": unit['theme'],
                        "word_count": unit['word_count']
                    },
                    "error": str(e)
                })

        return unit_analyses

    def _build_unit_analysis_prompt(
        self,
        unit_content: str,
        character_settings: List,
        unit: Dict
    ) -> str:
        """构建单元分析提示词"""
        chars_summary = "\n".join([
            f"- {char[:50]}..." for char in character_settings[:5]
        ])

        prompt = f"""
请对以下剧情单元进行5维拆解：

【单元信息】
- 单元编号：{unit['unit_number']}
- 章节范围：{unit['chapter_range']}
- 核心主题：{unit['theme']}
- 字数：{unit['word_count']}

【角色背景】
{chars_summary if character_settings else '（无角色信息）'}

【单元内容】
{unit_content[:3000]}...

请按以下格式输出：

## 一、单元大纲设计
（对应参考平台「大纲设计」模块，按情节推进顺序，清晰描述核心事件、关键转折、人物行动、冲突爆发、收尾钩子）

## 二、单元世界观设计
（对应参考平台「世界观设计」模块，分点拆解本单元中，世界观、力量体系、核心设定的展现、补充、推进）

## 三、单元人物塑造设计
（对应参考平台「人物塑造设计」模块，分点拆解本单元的核心人物关系、关系演进过程、人物弧光推进）

## 四、单元情绪设计
（对应参考平台「情绪设计」模块，分点拆解本单元的每个情绪节点，包含情绪类型、铺垫逻辑、爆发时机）

## 五、单元角色设计校验
（适配改编补充模块，明确本单元中，每个核心角色的行为是否符合全书总人设）
"""
        return prompt

    def _micro_analysis(
        self,
        file_data: Dict
    ) -> List[Dict]:
        """
        阶段4：底层微观拆书 - 单章细纲全维度拆解

        Args:
            file_data: 文件数据

        Returns:
            章节分析列表
        """
        chapters = file_data['chapters']
        chapter_analyses = []

        for chapter in chapters:
            chapter_content = chapter['content']

            # 构建分析提示
            prompt = self._build_chapter_analysis_prompt(
                chapter['title'],
                chapter_content
            )

            # 调用 LLM
            try:
                response = self.llm_client.generate(prompt)

                analysis = {
                    "chapter_number": chapter['chapter_number'],
                    "chapter_title": chapter['title'],
                    "word_count": len(chapter_content),
                    "本章核心定位": self._extract_section(response, "本章核心定位"),
                    "本章剧情细纲": self._extract_section(response, "本章剧情细纲"),
                    "本章核心创作逻辑拆解": self._extract_section(response, "本章核心创作逻辑拆解"),
                    "改编适配校验": self._extract_section(response, "改编适配校验")
                }

                chapter_analyses.append(analysis)

            except Exception as e:
                logger.error(f"章节 {chapter['chapter_number']} 分析失败: {e}")

        return chapter_analyses

    def _build_chapter_analysis_prompt(
        self,
        chapter_title: str,
        chapter_content: str
    ) -> str:
        """构建章节分析提示词"""
        prompt = f"""
请为以下章节生成详细细纲：

【章节标题】
{chapter_title}

【章节内容】
{chapter_content[:4000]}...

请按以下格式输出：

## 一、本章核心定位
- 在全书中的作用
- 本章核心目标
- 本章核心冲突
- 与前后章联动

## 二、本章剧情细纲
1. 开篇铺垫
2. 事件触发/核心转折
3. 情节推进/冲突升级
4. 爽点/高潮爆发
5. 结尾钩子

## 三、本章核心创作逻辑拆解
- 爽点设计
- 节奏设计
- 人设塑造
- 世界观展现

## 四、改编适配校验
- 本章核心不可替换的剧情骨架
- 可替换/改编的内容
- 人设适配要点
"""
        return prompt

    def _extract_section(self, text: str, section_name: str) -> str:
        """从LLM响应中提取特定章节内容"""
        pattern = rf'##\s*{re.escape(section_name)}\s*\n(.*?)(?=##\s*|$)'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""

    def _parse_file(self, file_path: str) -> Dict:
        """解析文件"""
        # 这里可以复用现有的文件解析逻辑
        # 简化版：假设已有解析函数
        return {
            "filename": Path(file_path).name,
            "content": "文件内容...",
            "total_chapters": 10  # 示例值
        }


# 便捷函数
def optimized_analyze_book_file(
    file_path: str,
    llm_client,
    chunking_strategy: str = "hybrid",
    chunk_size: int = 1000,
    use_mineru: bool = False,
    **options
) -> Dict:
    """
    便捷函数：使用优化版分析器分析书籍文件

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
    analyzer = OptimizedBookAnalyzer(
        llm_client=llm_client,
        chunking_strategy=chunking_strategy,
        chunk_size=chunk_size,
        use_mineru=use_mineru
    )

    return analyzer.analyze_book(file_path, options)