"""
增强版文本分块器 - 智能章节检测与语义分块
支持多种分块策略，可集成MinerU进行高质量文档解析
"""

import re
import hashlib
from typing import List, Dict, Tuple, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import logging

# 尝试导入MinerU（可选依赖）
try:
    from mineru import parse_document
    MINERU_AVAILABLE = True
except ImportError:
    MINERU_AVAILABLE = False
    logging.warning("MinerU not available, using fallback methods")

# 尝试导入中文分词
try:
    import jieba
    from jieba.analyse import TFIDF
    JIEBA_AVAILABLE = True
except ImportError:
    JIEBA_AVAILABLE = False
    logging.warning("jieba not available, text analysis may be limited")


class ChunkStrategy(Enum):
    """分块策略枚举"""
    CHAPTER = "chapter"          # 按章节分块
    SEMANTIC = "semantic"        # 语义分块（基于句子边界）
    FIXED_SIZE = "fixed_size"    # 固定大小分块
    ADAPTIVE = "adaptive"        # 自适应分块（结合章节和语义）
    HYBRID = "hybrid"            # 混合策略（章节内语义分块）


@dataclass
class Chunk:
    """文本分块数据类"""
    id: str
    content: str
    chunk_type: str
    metadata: Dict
    start_pos: int
    end_pos: int
    word_count: int

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "type": self.chunk_type,
            "metadata": self.metadata,
            "start_pos": self.start_pos,
            "end_pos": self.end_pos,
            "word_count": self.word_count
        }


class EnhancedTextChunker:
    """
    增强版文本分块器

    主要特性：
    1. 智能章节检测（多种模式匹配）
    2. 语义感知分块（保持句子完整性）
    3. 上下文保留（重叠窗口）
    4. MinerU集成（高质量文档解析）
    5. 自适应分块策略
    """

    def __init__(
        self,
        strategy: ChunkStrategy = ChunkStrategy.HYBRID,
        chunk_size: int = 1000,
        overlap: int = 100,
        use_mineru: bool = True,
        enable_semantic: bool = True
    ):
        self.strategy = strategy
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.use_mineru = use_mineru and MINERU_AVAILABLE
        self.enable_semantic = enable_semantic

        # 中文句子分割模式
        self.sentence_pattern = re.compile(
            r'[^。！？；\n]+[。！？；\n]+|[^。！？；\n]+$',
            re.MULTILINE
        )

        # 章节检测模式（按优先级排序）
        self.chapter_patterns = [
            # 高优先级：标准章节格式
            (r'\n\s*第[一二三四五六七八九十百千万\d]+[章节回幕][^\n]*', 100),
            (r'\n\s*Chapter\s*\d+[^\n]*', 95),
            (r'\n\s*第[一二三四五六七八九十百千万\d]+部分[^\n]*', 90),

            # 中优先级：数字编号
            (r'\n\s*\d+[\.、][^\n]+', 70),
            (r'\n\s*[一二三四五六七八九十]+[、\.][^\n]+', 70),

            # 低优先级：其他格式
            (r'\n\s*[卷篇集][^\n]+', 50),
            (r'\n\s*【[^\n]+】', 40),
            (r'\n\s*\[[^\n]+\]', 40),
        ]

        # 初始化TFIDF用于语义分析
        if JIEBA_AVAILABLE and enable_semantic:
            self.tfidf = TFIDF()
        else:
            self.tfidf = None

        self.logger = logging.getLogger(__name__)

    def chunk_text(
        self,
        text: str,
        metadata: Optional[Dict] = None
    ) -> List[Chunk]:
        """
        主分块入口

        Args:
            text: 输入文本
            metadata: 元数据信息

        Returns:
            分块列表
        """
        if metadata is None:
            metadata = {}

        self.logger.info(f"Starting text chunking with strategy: {self.strategy.value}")

        # 预处理：清理文本
        cleaned_text = self._preprocess_text(text)

        # 根据策略选择分块方法
        if self.strategy == ChunkStrategy.CHAPTER:
            chunks = self._chunk_by_chapter(cleaned_text, metadata)
        elif self.strategy == ChunkStrategy.SEMANTIC:
            chunks = self._chunk_semantic(cleaned_text, metadata)
        elif self.strategy == ChunkStrategy.FIXED_SIZE:
            chunks = self._chunk_fixed_size(cleaned_text, metadata)
        elif self.strategy == ChunkStrategy.ADAPTIVE:
            chunks = self._chunk_adaptive(cleaned_text, metadata)
        elif self.strategy == ChunkStrategy.HYBRID:
            chunks = self._chunk_hybrid(cleaned_text, metadata)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

        # 添加语义元数据
        if self.enable_semantic and JIEBA_AVAILABLE:
            chunks = self._add_semantic_metadata(chunks)

        self.logger.info(f"Text chunking completed: {len(chunks)} chunks generated")
        return chunks

    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        # 统一换行符
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # 去除多余空行（保留最多2个连续空行）
        text = re.sub(r'\n{4,}', '\n\n\n', text)

        # 规范化空格
        text = re.sub(r'[ \t]+', ' ', text)

        return text.strip()

    def _chunk_by_chapter(
        self,
        text: str,
        metadata: Dict
    ) -> List[Chunk]:
        """按章节分块"""
        chapters = self._detect_chapters(text)

        if not chapters:
            self.logger.warning("No chapters detected, falling back to semantic chunking")
            return self._chunk_semantic(text, metadata)

        chunks = []
        current_pos = 0

        for i, (title, content, start, end) in enumerate(chapters):
            chunk_id = self._generate_chunk_id("chapter", i, title)
            chunk_metadata = {
                **metadata,
                "chapter_number": i + 1,
                "chapter_title": title,
                "chunk_type": "chapter"
            }

            chunk = Chunk(
                id=chunk_id,
                content=content,
                chunk_type="chapter",
                metadata=chunk_metadata,
                start_pos=start,
                end_pos=end,
                word_count=len(content)
            )

            chunks.append(chunk)
            current_pos = end

        return chunks

    def _chunk_semantic(
        self,
        text: str,
        metadata: Dict
    ) -> List[Chunk]:
        """语义分块 - 保持句子完整性"""
        sentences = list(self.sentence_pattern.finditer(text))

        if not sentences:
            # 如果没有找到句子，按字符分割
            return self._chunk_fixed_size(text, metadata)

        chunks = []
        current_chunk_sentences = []
        current_length = 0
        chunk_index = 0

        for sentence_match in sentences:
            sentence = sentence_match.group()

            # 检查添加这个句子是否会超出限制
            if current_length + len(sentence) > self.chunk_size and current_chunk_sentences:
                # 创建当前分块
                chunk_id = self._generate_chunk_id("semantic", chunk_index)
                chunk_content = ''.join(current_chunk_sentences)

                chunk = Chunk(
                    id=chunk_id,
                    content=chunk_content.strip(),
                    chunk_type="semantic",
                    metadata={**metadata, "chunk_type": "semantic"},
                    start_pos=sentences[0].start() if chunks else 0,
                    end_pos=sentence_match.end(),
                    word_count=len(chunk_content)
                )
                chunks.append(chunk)
                chunk_index += 1

                # 重置，添加重叠
                overlap_sentences = self._get_overlap_sentences(
                    current_chunk_sentences,
                    target_length=self.overlap
                )
                current_chunk_sentences = overlap_sentences
                current_length = sum(len(s) for s in current_chunk_sentences)

            current_chunk_sentences.append(sentence)
            current_length += len(sentence)

        # 添加最后一个分块
        if current_chunk_sentences:
            chunk_id = self._generate_chunk_id("semantic", chunk_index)
            chunk_content = ''.join(current_chunk_sentences)

            chunk = Chunk(
                id=chunk_id,
                content=chunk_content.strip(),
                chunk_type="semantic",
                metadata={**metadata, "chunk_type": "semantic"},
                start_pos=sentences[0].start() if not chunks else chunks[-1].end_pos,
                end_pos=sentences[-1].end() if sentences else len(text),
                word_count=len(chunk_content)
            )
            chunks.append(chunk)

        return chunks

    def _chunk_fixed_size(
        self,
        text: str,
        metadata: Dict
    ) -> List[Chunk]:
        """固定大小分块（带重叠）"""
        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))

            # 尝试在句子边界处分割
            if end < len(text):
                last_sentence_boundary = text.rfind('。', start, end)
                if last_sentence_boundary > start + self.chunk_size // 2:
                    end = last_sentence_boundary + 1

            chunk_id = self._generate_chunk_id("fixed", chunk_index)
            content = text[start:end]

            chunk = Chunk(
                id=chunk_id,
                content=content.strip(),
                chunk_type="fixed_size",
                metadata={**metadata, "chunk_type": "fixed_size"},
                start_pos=start,
                end_pos=end,
                word_count=len(content)
            )
            chunks.append(chunk)

            start = end - self.overlap
            chunk_index += 1

        return chunks

    def _chunk_adaptive(
        self,
        text: str,
        metadata: Dict
    ) -> List[Chunk]:
        """自适应分块 - 根据内容密度调整大小"""
        # 检测章节
        chapters = self._detect_chapters(text)

        if not chapters:
            return self._chunk_semantic(text, metadata)

        chunks = []

        for i, (title, content, start, end) in enumerate(chapters):
            # 计算内容密度（段落数/字数比）
            paragraph_count = len([p for p in content.split('\n\n') if p.strip()])
            density = paragraph_count / max(len(content), 1)

            # 根据密度调整分块大小
            adaptive_size = int(self.chunk_size * (0.5 + density))

            if len(content) <= adaptive_size * 1.5:
                # 章节足够小，直接作为一个分块
                chunk_id = self._generate_chunk_id("adaptive", f"chapter_{i}", title)
                chunk = Chunk(
                    id=chunk_id,
                    content=content,
                    chunk_type="adaptive",
                    metadata={**metadata, "chapter_number": i + 1, "chapter_title": title},
                    start_pos=start,
                    end_pos=end,
                    word_count=len(content)
                )
                chunks.append(chunk)
            else:
                # 章节太长，使用语义分块
                sub_chunks = self._chunk_semantic(
                    content,
                    {**metadata, "chapter_number": i + 1, "chapter_title": title}
                )

                # 调整分块的绝对位置
                chapter_offset = start
                for sub_chunk in sub_chunks:
                    sub_chunk.start_pos += chapter_offset
                    sub_chunk.end_pos += chapter_offset
                    chunks.append(sub_chunk)

        return chunks

    def _chunk_hybrid(
        self,
        text: str,
        metadata: Dict
    ) -> List[Chunk]:
        """混合策略 - 章节检测 + 章节内语义分块"""
        chapters = self._detect_chapters(text)

        if not chapters:
            self.logger.warning("No chapters detected, using semantic chunking")
            return self._chunk_semantic(text, metadata)

        chunks = []

        for i, (title, content, start, end) in enumerate(chapters):
            # 章节元数据
            chapter_metadata = {
                **metadata,
                "chapter_number": i + 1,
                "chapter_title": title,
                "chunk_type": "hybrid"
            }

            # 如果章节长度适中，直接作为一个分块
            if len(content) <= self.chunk_size * 2:
                chunk_id = self._generate_chunk_id("hybrid", f"chapter_{i}", title)
                chunk = Chunk(
                    id=chunk_id,
                    content=content,
                    chunk_type="hybrid",
                    metadata=chapter_metadata,
                    start_pos=start,
                    end_pos=end,
                    word_count=len(content)
                )
                chunks.append(chunk)
            else:
                # 章节较长，进行语义分块
                sub_chunks = self._chunk_semantic(content, chapter_metadata)

                # 调整位置信息
                for sub_chunk in sub_chunks:
                    sub_chunk.start_pos += start
                    sub_chunk.end_pos += start
                    chunks.append(sub_chunk)

        return chunks

    def _detect_chapters(
        self,
        text: str
    ) -> List[Tuple[str, str, int, int]]:
        """
        智能检测章节

        Returns:
            List of (title, content, start_pos, end_pos)
        """
        self.logger.info("Starting chapter detection")

        # 使用加权评分系统
        candidates = []

        for pattern, score in self.chapter_patterns:
            matches = list(re.finditer(pattern, text))
            for match in matches:
                candidates.append({
                    "pattern": pattern,
                    "score": score,
                    "match": match
                })

        # 如果没有找到任何候选，返回空列表
        if not candidates:
            self.logger.warning("No chapter candidates found")
            return []

        # 按位置和评分排序
        candidates.sort(key=lambda x: (x["match"].start(), -x["score"]))

        # 选择最佳章节标记（避免重叠）
        selected_chapters = []
        min_gap = 500  # 两个章节标记之间的最小距离（字符）

        for candidate in candidates:
            match = candidate["match"]

            # 检查是否与已选章节冲突
            conflict = False
            for selected in selected_chapters:
                if abs(match.start() - selected["start"]) < min_gap:
                    # 选择评分更高的
                    if candidate["score"] > selected["score"]:
                        selected_chapters.remove(selected)
                    else:
                        conflict = True
                    break

            if not conflict:
                selected_chapters.append({
                    "title": match.group().strip(),
                    "start": match.start(),
                    "end": match.end(),
                    "score": candidate["score"]
                })

        # 按位置排序
        selected_chapters.sort(key=lambda x: x["start"])

        # 提取章节内容
        chapters = []
        for i, chapter in enumerate(selected_chapters):
            start = chapter["end"]
            title = chapter["title"]

            # 确定章节结束位置
            if i < len(selected_chapters) - 1:
                end = selected_chapters[i + 1]["start"]
            else:
                end = len(text)

            # 提取内容
            content = text[start:end].strip()

            if content:  # 只保留有内容的章节
                chapters.append((title, content, chapter["start"], end))

        self.logger.info(f"Detected {len(chapters)} chapters")
        return chapters

    def _get_overlap_sentences(
        self,
        sentences: List[str],
        target_length: int
    ) -> List[str]:
        """获取重叠的句子"""
        if not sentences:
            return []

        overlap_sentences = []
        total_length = 0

        # 从末尾开始添加句子
        for sentence in reversed(sentences):
            if total_length + len(sentence) <= target_length:
                overlap_sentences.insert(0, sentence)
                total_length += len(sentence)
            else:
                break

        return overlap_sentences

    def _generate_chunk_id(
        self,
        chunk_type: str,
        index: int,
        title: Optional[str] = None
    ) -> str:
        """生成唯一的分块ID"""
        base = f"{chunk_type}_{index}"
        if title:
            # 使用标题的哈希作为后缀
            title_hash = hashlib.md5(title.encode()).hexdigest()[:8]
            base = f"{base}_{title_hash}"
        return base

    def _add_semantic_metadata(self, chunks: List[Chunk]) -> List[Chunk]:
        """添加语义元数据（关键词、主题等）"""
        for chunk in chunks:
            if len(chunk.content) < 100:
                continue

            try:
                # 提取关键词
                keywords = self.tfidf.extract_tags(chunk.content, topK=5, withWeight=False)
                chunk.metadata["keywords"] = keywords

                # 简单的主题检测（基于关键词）
                if keywords:
                    chunk.metadata["topic"] = ", ".join(keywords[:3])

            except Exception as e:
                self.logger.warning(f"Failed to add semantic metadata: {e}")

        return chunks

    def parse_with_mineru(self, file_path: str) -> Optional[Dict]:
        """
        使用MinerU解析文档

        Args:
            file_path: 文档路径

        Returns:
            解析后的文档数据，如果MinerU不可用则返回None
        """
        if not self.use_mineru:
            self.logger.warning("MinerU not enabled or available")
            return None

        try:
            self.logger.info(f"Parsing document with MinerU: {file_path}")
            result = parse_document(file_path)

            # MinerU返回的结果结构可能不同，这里需要根据实际API调整
            return {
                "text": result.get("text", ""),
                "structure": result.get("structure", []),
                "metadata": result.get("metadata", {})
            }

        except Exception as e:
            self.logger.error(f"MinerU parsing failed: {e}")
            return None

    def chunk_document(
        self,
        file_path: str,
        metadata: Optional[Dict] = None
    ) -> List[Chunk]:
        """
        完整的文档分块流程

        Args:
            file_path: 文档路径
            metadata: 元数据

        Returns:
            分块列表
        """
        if metadata is None:
            metadata = {}

        # 尝试使用MinerU
        mineru_result = self.parse_with_mineru(file_path)

        if mineru_result:
            self.logger.info("Using MinerU parsed content")
            text = mineru_result["text"]

            # 合并MinerU的元数据
            if "metadata" in mineru_result:
                metadata.update(mineru_result["metadata"])
        else:
            # 回退到普通文本读取
            self.logger.info("Reading document as plain text")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
            except UnicodeDecodeError:
                # 尝试其他编码
                try:
                    with open(file_path, 'r', encoding='gbk') as f:
                        text = f.read()
                except Exception as e:
                    self.logger.error(f"Failed to read file: {e}")
                    return []

        # 添加文件路径到元数据
        metadata["source_file"] = file_path

        # 执行分块
        return self.chunk_text(text, metadata)


# 便捷函数
def chunk_text_file(
    file_path: str,
    strategy: str = "hybrid",
    chunk_size: int = 1000,
    overlap: int = 100,
    **kwargs
) -> List[Dict]:
    """
    便捷函数：直接对文件进行分块

    Args:
        file_path: 文件路径
        strategy: 分块策略 (chapter/semantic/fixed_size/adaptive/hybrid)
        chunk_size: 分块大小
        overlap: 重叠大小

    Returns:
        分块字典列表
    """
    strategy_enum = ChunkStrategy(strategy)
    chunker = EnhancedTextChunker(
        strategy=strategy_enum,
        chunk_size=chunk_size,
        overlap=overlap,
        **kwargs
    )

    chunks = chunker.chunk_document(file_path)
    return [chunk.to_dict() for chunk in chunks]


# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # 示例1：简单文本分块
    sample_text = """
    第一章 开始

    这是第一章的内容，包含多个句子。
    这里有第二句话。还有第三句。

    第二章 继续

    这是第二章的内容。
    也包含一些描述性文字。
    """

    chunker = EnhancedTextChunker(strategy=ChunkStrategy.HYBRID)
    chunks = chunker.chunk_text(sample_text)

    print(f"生成了 {len(chunks)} 个分块:")
    for i, chunk in enumerate(chunks, 1):
        print(f"\n分块 {i}:")
        print(f"  类型: {chunk.chunk_type}")
        print(f"  字数: {chunk.word_count}")
        print(f"  内容预览: {chunk.content[:50]}...")
        if "chapter_title" in chunk.metadata:
            print(f"  章节: {chunk.metadata['chapter_title']}")

    # 示例2：对文件进行分块
    # chunks = chunk_text_file("your_novel.txt", strategy="hybrid")
