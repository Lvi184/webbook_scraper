import re
import jieba
from typing import List, Dict, Tuple
from collections import Counter

class TextProcessor:
    """文本处理服务 - 中文文本分块和关键词提取"""

    def __init__(self):
        # 常见的中文标点符号
        self.punctuation = '。！？；：""''（）【】《》'
        self.sentence_pattern = re.compile(r'[。！？；\n]+')

    def split_into_units(self, chapters: List[Dict], unit_size: int = 5) -> List[Dict]:
        """将章节合并为剧情单元（默认5章/单元）"""
        units = []
        current_unit = []
        current_word_count = 0

        for chapter in chapters:
            current_unit.append(chapter)
            current_word_count += chapter['word_count']

            # 达到单元大小时，保存当前单元
            if current_word_count >= unit_size * 1000 or len(current_unit) >= unit_size:
                unit_content = ''
                unit_range = []
                unit_theme = ''

                for ch in current_unit:
                    unit_content += ch['content'] + '\n'
                    unit_range.append(ch['chapter_number'])

                # 生成单元主题
                unit_theme = self._generate_unit_theme(current_unit)

                units.append({
                    "unit_number": len(units) + 1,
                    "chapter_range": unit_range,
                    "theme": unit_theme,
                    "content": unit_content,
                    "word_count": current_word_count,
                    "chapters": current_unit
                })

                # 重置当前单元
                current_unit = []
                current_word_count = 0

        # 添加最后一个不完整的单元
        if current_unit:
            unit_content = ''
            unit_range = []
            unit_theme = ''

            for ch in current_unit:
                unit_content += ch['content'] + '\n'
                unit_range.append(ch['chapter_number'])

            unit_theme = self._generate_unit_theme(current_unit)

            units.append({
                "unit_number": len(units) + 1,
                "chapter_range": unit_range,
                "theme": unit_theme,
                "content": unit_content,
                "word_count": current_word_count,
                "chapters": current_unit
            })

        return units

    def _generate_unit_theme(self, chapters: List[Dict]) -> str:
        """生成单元主题"""
        # 提取所有章节的标题
        titles = [ch['title'] for ch in chapters]

        # 提取关键词
        all_text = ' '.join([ch['content'] for ch in chapters])
        keywords = self.extract_keywords(all_text, top_k=5)

        # 简单的主题生成
        if len(titles) > 0:
            theme = f"{titles[0]}-{titles[-1]} - {','.join(keywords[:3])}"
        else:
            theme = f"单元{chapters[0]['chapter_number']}-{chapters[-1]['chapter_number']}"

        return theme

    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """提取关键词"""
        # 使用jieba分词
        words = jieba.cut(text)

        # 过滤
        filtered_words = [
            word.strip() for word in words
            if len(word) > 1 and word not in self.punctuation
            and not word.isdigit()
        ]

        # 统计词频
        word_freq = Counter(filtered_words)

        return [word for word, freq in word_freq.most_common(top_k)]

    def split_content_into_blocks(self, content: str, block_size: int = 1000) -> List[str]:
        """将内容分块"""
        blocks = []

        # 先按句子分割
        sentences = self.sentence_pattern.split(content)
        sentences = [s.strip() for s in sentences if s.strip()]

        current_block = ""

        for sentence in sentences:
            if len(current_block) + len(sentence) <= block_size:
                current_block += sentence + "。"
            else:
                if current_block:
                    blocks.append(current_block.strip())
                current_block = sentence + "。"

        if current_block:
            blocks.append(current_block.strip())

        return blocks