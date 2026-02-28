# 文本分块解决方案 - 快速入门

## 概述

本文档为你提供了一套完整的中文网文智能分块解决方案，包括：

1. **enhanced_text_chunker.py** - 核心分块引擎
2. **book_analyzer_v2.py** - 集成到书籍分析的增强版分析器
3. **text_chunking_examples.py** - 完整使用示例

## 方案对比

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **原始方案** (file_parser.py) | 简单、依赖少 | 仅正则匹配、不够智能 | 简单文档 |
| **增强方案** (enhanced_text_chunker.py) | 智能分块、多策略、语义感知 | 依赖较多 | 网文分析、复杂文档 |
| **MinerU集成** | 高质量解析、支持复杂格式 | 安装较复杂、可能较慢 | PDF、扫描件 |

## 快速开始

### 1. 安装依赖

```bash
# 基础安装（必需）
pip install jieba

# 可选：安装MinerU用于高质量文档解析
pip install git+https://github.com/opendatalab/MinerU.git
```

### 2. 基础使用

```python
from enhanced_text_chunker import EnhancedTextChunker, ChunkStrategy

# 创建分块器（推荐使用HYBRID策略）
chunker = EnhancedTextChunker(
    strategy=ChunkStrategy.HYBRID,
    chunk_size=1000,
    enable_semantic=True
)

# 对文本进行分块
text = """
第一章 开始
这是第一章的内容...
第二章 继续
这是第二章的内容...
"""

chunks = chunker.chunk_text(text)

# 查看结果
for chunk in chunks:
    print(f"类型: {chunk.chunk_type}")
    print(f"章节: {chunk.metadata.get('chapter_title')}")
    print(f"内容: {chunk.content[:100]}...")
```

### 3. 文件分块

```python
from enhanced_text_chunker import chunk_text_file

# 一行代码完成文件分块
chunks = chunk_text_file(
    "your_novel.txt",
    strategy="hybrid",
    chunk_size=1500
)

# chunks是字典列表，可直接使用或导出
import json
with open('result.json', 'w', encoding='utf-8') as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)
```

## 分块策略选择

| 策略 | 说明 | 推荐场景 |
|------|------|----------|
| **CHAPTER** | 按章节分块 | 有明显章节结构的网文 |
| **SEMANTIC** | 语义分块（保持句子完整） | 无章节、强调语义连贯性 |
| **FIXED_SIZE** | 固定大小分块 | 简单场景、需要均匀分块 |
| **ADAPTIVE** | 自适应分块（根据密度调整） | 内容密度不均匀 |
| **HYBRID** ⭐ | 章节+语义混合 | 大多数网文（推荐） |

## 集成到现有项目

### 方式1：直接替换（推荐）

在现有的 `book_analyzer.py` 中，将分块部分替换为：

```python
from .enhanced_text_chunker import EnhancedTextChunker, ChunkStrategy

class BookAnalyzer:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        # 使用增强版分块器
        self.chunker = EnhancedTextChunker(
            strategy=ChunkStrategy.HYBRID,
            chunk_size=1000,
            enable_semantic=True
        )

    def analyze_book(self, file_data: Dict) -> Dict:
        # 使用增强版分块
        chunks = self.chunker.chunk_text(
            file_data['content'],
            metadata={'filename': file_data['filename']}
        )
        # ... 后续处理 ...
```

### 方式2：使用BookAnalyzerV2

```python
from .book_analyzer_v2 import BookAnalyzerV2

# 创建分析器
analyzer = BookAnalyzerV2(
    llm_client=your_llm_client,
    chunking_strategy="hybrid",
    chunk_size=1000,
    use_mineru=True  # 可选
)

# 执行分析
result = analyzer.analyze_book("your_novel.txt")
```

## MinerU 集成

### 安装

```bash
# 方法1：pip安装
pip install mineru

# 方法2：从源码安装（推荐）
pip install git+https://github.com/opendatalab/MinerU.git
```

### 使用

```python
# 启用MinerU
chunker = EnhancedTextChunker(
    strategy=ChunkStrategy.HYBRID,
    use_mineru=True  # 尝试使用MinerU
)

# 如果MinerU不可用，会自动回退
chunks = chunker.chunk_document("your_document.pdf")
```

### 检查可用性

```python
from enhanced_text_chunker import MINERU_AVAILABLE

if MINERU_AVAILABLE:
    print("✓ MinerU 可用")
else:
    print("✗ MinerU 不可用，将使用回退方法")
```

## 常见问题

### Q1: chunk_size 设置多大合适？

根据你的LLM上下文窗口：

| LLM模型 | 上下文窗口 | 推荐chunk_size |
|---------|------------|----------------|
| GPT-3.5 | 4K-16K | 1000-2000 |
| GPT-4 | 8K-128K | 1500-4000 |
| Claude-3 | 200K | 2000-5000 |
| 本地模型 | 2K-8K | 500-1000 |

### Q2: 章节检测不准确怎么办？

1. 添加自定义章节模式：
```python
chunker.chapter_patterns.append(
    (r'\n\s*你的自定义格式[^\n]*', 80)
)
```

2. 使用 SEMANTIC 策略代替 CHAPTER

### Q3: 处理大文件时内存不够？

使用分块处理：

```python
def process_large_file(file_path):
    chunker = EnhancedTextChunker(strategy=ChunkStrategy.CHAPTER)

    # 先检测章节
    with open(file_path, 'r', encoding='utf-8') as f:
        chapters = chunker._detect_chapters(f.read())

    # 逐章处理
    for title, content, start, end in chapters:
        # 处理单个章节...
        pass
```

## 性能优化建议

1. **缓存分块结果** - 避免重复处理同一文件
2. **并行处理** - 各章节可并行分块
3. **按需加载** - 大文件使用流式处理
4. **选择合适策略** - 简单文档用FIXED_SIZE，复杂文档用HYBRID

## 示例代码位置

- 基础示例：`examples/text_chunking_examples.py`
- 详细指南：`docs/TEXT_CHUNKING_GUIDE.md`
- 核心模块：`services/enhanced_text_chunker.py`

## 下一步

1. 运行示例：`python examples/text_chunking_examples.py`
2. 阅读详细指南：`docs/TEXT_CHUNKING_GUIDE.md`
3. 集成到你的项目中

## 技术支持

如遇问题，请检查：
1. jieba是否正确安装
2. 文件编码是否为UTF-8
3. 日志输出中的错误信息
