import re
import json
from typing import List, Dict, Any
from .text_processor import TextProcessor

class BookAnalyzer:
    """四阶段拆书分析器"""

    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.text_processor = TextProcessor()

    def analyze_book(self, file_data: Dict) -> Dict:
        """执行四阶段拆书分析"""
        chapters = file_data['chapters']

        # 阶段1：前置预处理 - 剧情单元划分
        units = self.stage1_preprocessing(chapters)

        # 阶段2：顶层宏观拆书 - 核心总纲
        world_outline, main_plot, character_settings = self.stage2_macro_analysis(units)

        # 确保character_settings是列表
        if character_settings is None:
            character_settings = []

        # 阶段3：中层中观拆书 - 单元5维分析
        unit_analyses = self.stage3_middle_analysis(units, character_settings)

        # 阶段4：底层微观拆书 - 单章细纲
        chapter_analyses = self.stage4_micro_analysis(chapters)

        # 汇总结果
        result = {
            "book_info": {
                "filename": file_data['filename'],
                "total_chapters": file_data.get('total_chapters', len(chapters)),
                "total_units": len(units)
            },
            "stage1_units": units,
            "stage2_world_outline": world_outline,
            "stage2_main_plot": main_plot,
            "stage2_characters": character_settings,
            "stage3_units_analysis": unit_analyses,
            "stage4_chapters_analysis": chapter_analyses
        }

        return result

    def stage1_preprocessing(self, chapters: List[Dict]) -> List[Dict]:
        """阶段1：前置预处理 - 剧情单元划分"""
        # 按5章/单元分割
        units = self.text_processor.split_into_units(chapters, unit_size=5)

        # 补充单元详细信息
        for unit in units:
            # 提取单元关键词
            unit['keywords'] = self.text_processor.extract_keywords(unit['content'], top_k=10)

        return units

    def stage2_macro_analysis(self, units: List[Dict]) -> tuple:
        """阶段2：顶层宏观拆书"""
        # 生成世界观总纲
        world_outline = self._analyze_world_outline(units)

        # 生成核心大纲
        main_plot = self._analyze_main_plot(units)

        # 生成角色总设定
        character_settings = self._analyze_characters(units)

        return world_outline, main_plot, character_settings

    def _analyze_world_outline(self, units: List[Dict]) -> Dict:
        """分析世界观总纲（5个维度）"""
        content = '\n'.join([unit['content'] for unit in units])

        prompt = f"""
        请根据以下小说内容，分析世界观总纲，包含以下5个维度：

        1. 基础时空背景：故事发生的世界、时代、核心环境
        2. 核心力量体系：分阶拆解能力层级、突破规则
        3. 核心势力划分：主要阵营/势力、对立/合作关系
        4. 世界核心规则/铁则：必须遵守的底层限制
        5. 核心差异化设定：最独特的核心卖点

        小说内容：
        {content[:5000]}

        请用JSON格式返回，包含上述5个键。
        """

        response = self.llm_client.generate(prompt)
        return self._parse_json_response(response)

    def _analyze_main_plot(self, units: List[Dict]) -> Dict:
        """分析核心大纲"""
        content = '\n'.join([unit['content'] for unit in units])

        prompt = f"""
        请根据以下小说内容，分析全本核心大纲：

        1. 一句话完整概括：主角初始状态→核心目标→核心冲突→最终结局
        2. 全书核心剧情节点（按时间线）：
           - 开篇起点
           - 第一转折点
           - 中期核心冲突
           - 全书高潮节点
           - 结局落点

        小说内容：
        {content[:5000]}

        请用JSON格式返回。
        """

        response = self.llm_client.generate(prompt)
        return self._parse_json_response(response)

    def _analyze_characters(self, units: List[Dict]) -> List[Dict]:
        """分析核心角色总设定（7个维度）"""
        content = '\n'.join([unit['content'] for unit in units])

        prompt = f"""
        请提取小说中的核心角色（主角+反派+关键配角），每个角色分析以下7个维度：

        1. 属性标签：核心性格标签
        2. 基本信息：年龄、身份、身世背景、关系
        3. 核心人设：性格、价值观、行为准则、执念
        4. 核心功能：在剧情中的定位、推动作用
        5. 核心能力/金手指：能力、规则、限制
        6. 人物弧光：从开篇到结局的成长线
        7. 外貌气质：原文中的外貌描述

        小说内容：
        {content[:5000]}

        请用JSON数组格式返回，每个角色一个对象。
        """

        response = self.llm_client.generate(prompt)
        return self._parse_json_response(response)

    def stage3_middle_analysis(self, units: List[Dict], characters: List[Dict]) -> List[Dict]:
        """阶段3：中层中观拆书 - 单元5维分析"""
        unit_analyses = []

        for unit in units:
            unit_analysis = self._analyze_unit_5d(unit, characters)
            unit_analyses.append(unit_analysis)

        return unit_analyses

    def _analyze_unit_5d(self, unit: Dict, characters: List[Dict]) -> Dict:
        """分析单元的5个维度"""
        content = unit['content']

        prompt = f"""
        请分析这个剧情单元的5个维度：

        1. 单元大纲设计：完整剧情拆解、关键转折、冲突、收尾
        2. 单元世界观设计：设定展现、补充、对剧情推动
        3. 单元人物塑造设计：关系演进、弧光推进、情感节点
        4. 单元情绪设计：情绪类型、铺垫、爆发、价值
        5. 单元角色设计校验：行为是否符合总人设

        单元内容：
        {content[:3000]}

        角色设定参考：
        {json.dumps(characters[:3] if isinstance(characters, list) and characters else [], ensure_ascii=False)}

        请用JSON格式返回。
        """

        response = self.llm_client.generate(prompt)
        analysis = self._parse_json_response(response)

        # 补充单元信息
        analysis['unit_number'] = unit['unit_number']
        analysis['chapter_range'] = unit['chapter_range']
        analysis['theme'] = unit['theme']

        return analysis

    def stage4_micro_analysis(self, chapters: List[Dict]) -> List[Dict]:
        """阶段4：底层微观拆书 - 单章细纲"""
        chapter_analyses = []

        for chapter in chapters[:20]:  # 限制前20章避免过长
            analysis = self._analyze_chapter(chapter)
            chapter_analyses.append(analysis)

        return chapter_analyses

    def _analyze_chapter(self, chapter: Dict) -> Dict:
        """分析单章细纲"""
        content = chapter['content']

        prompt = f"""
        请分析这章的细纲（4个维度）：

        1. 本章核心定位：
           - 在全书中的作用
           - 本章核心目标
           - 本章核心冲突
           - 与前后章联动

        2. 本章剧情细纲（按情节推进）：
           - 开篇铺垫
           - 事件触发/核心转折
           - 情节推进/冲突升级
           - 爽点/高潮爆发
           - 结尾钩子

        3. 本章核心创作逻辑：
           - 爽点设计
           - 节奏设计
           - 人设塑造
           - 世界观展现

        4. 改编适配校验：
           - 不可替换的剧情骨架
           - 可替换/改编的内容
           - 人设适配要点

        章节内容：
        {content[:2000]}

        请用JSON格式返回。
        """

        response = self.llm_client.generate(prompt)
        analysis = self._parse_json_response(response)

        # 补充章信息
        analysis['chapter_number'] = chapter['chapter_number']
        analysis['title'] = chapter['title']

        return analysis

    def _parse_json_response(self, response: str) -> Any:
        """解析JSON响应"""
        try:
            # 提取JSON部分 - 优先查找数组
            if '[' in response and ']' in response:
                json_start = response.find('[')
                json_end = response.rfind(']') + 1
            else:
                # 查找对象
                json_start = response.find('{')
                json_end = response.rfind('}') + 1

            if json_start == -1 or json_end == 0:
                return {"error": "无法解析JSON响应"}

            json_str = response[json_start:json_end]
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"error": "JSON解析失败", "raw_response": response}