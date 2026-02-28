# 文本分块器使用指南

## 概述

本文档介绍 `enhanced_text_chunker.py` 模块的使用方法，这是一个智能的中文文本分块工具，专为网文分析设计。

## 特性

- ✅ **智能章节检测** - 支持多种章节格式自动识别
- ✅ **语义感知分块** - 保持句子完整性，避免在句中分割
- ✅ **多种分块策略** - 章节分块、语义分块、固定分块、自适应分块、混合分块
- ✅ **上下文保留** - 可配置的重叠窗口，保持分块间的语义连贯性
- ✅ **MinerU集成** - 支持高质量文档解析（需安装）
- ✅ **中文支持** - 基于jieba的中文分词和关键词提取

## 安装依赖

```bash
# 基础依赖
pip install jieba

# 可选：MinerU（高质量文档解析）
pip install mineru

# 如果遇到问题，可以从源码安装
pip install git+https://github.com/opendatalab/MinerU.git
```

## 快速开始

### 基础使用

```python
from enhanced_text_chunker import EnhancedTextChunker, ChunkStrategy

# 创建分块器
chunker = EnhancedTextChunker(
    strategy=ChunkStrategy.HYBRID,  # 混合策略（推荐）
    chunk_size=1000,                 # 目标分块大小
    overlap=100,                     # 重叠大小
    enable_semantic=True            # 启用语义分析
)

# 对文本进行分块
text = "你的文本内容..."
chunks = chunker.chunk_text(text)

# 访问分块
for chunk in chunks:
    print(f"ID: {chunk.id}")
    print(f"内容: {chunk.content}")
    print(f"元数据: {chunk.metadata}")
```

### 对文件进行分块

```python
from enhanced_text_chunker import chunk_text_file

# 便捷函数
chunks = chunk_text_file(
    "your_novel.txt",
    strategy="hybrid",
    chunk_size=1500
)

# chunks 是字典列表
for chunk in chunks:
    print(chunk['content'])
```

## 分块策略

### 1. CHAPTER - 按章节分块

适用于有明显章节结构的网文。

```python
chunker = EnhancedTextChunker(strategy=ChunkStrategy.CHAPTER)
```

**支持的章节格式：**
- 第X章/节/卷/部分/幕
- Chapter X
- X. 格式编号
- 一、二、三... 中文数字编号

### 2. SEMANTIC - 语义分块

在句子边界处分割，保持语义完整性。

```python
chunker = EnhancedTextChunker(
    strategy=ChunkStrategy.SEMANTIC,
    chunk_size=1000,
    overlap=100  # 可选的重叠窗口
)
```

### 3. FIXED_SIZE - 固定大小分块

简单的按字符数分割，尽量在句子边界处断开。

```python
chunker = EnhancedTextChunker(
    strategy=ChunkStrategy.FIXED_SIZE,
    chunk_size=1000,
    overlap=100
)
```

### 4. ADAPTIVE - 自适应分块

根据内容密度（段落/字符比）自动调整分块大小。

```python
chunker = EnhancedTextChunker(
    strategy=ChunkStrategy.ADAPTIVE,
    chunk_size=1000
)
```

### 5. HYBRID - 混合策略（推荐）

先按章节检测，然后在章节内部使用语义分块。这是最智能的策略。

```python
chunker = EnhancedTextChunker(
    strategy=ChunkStrategy.HYBRID,
    chunk_size=1000,
    enable_semantic=True
)
```

## MinerU 集成

MinerU 是一个高质量的文档解析工具，能够更好地处理PDF、图片等复杂格式。

### 安装 MinerU

```bash
# 方法1：直接安装
pip install mineru

# 方法2：从源码安装（推荐）
pip install git+https://github.com/opendatalab/MinerU.git

# 或使用 conda
conda install -c conda-forge mineru
```

### 使用 MinerU

```python
# 创建分块器时启用 MinerU
chunker = EnhancedTextChunker(
    strategy=ChunkStrategy.HYBRID,
    use_mineru=True  # 尝试使用 MinerU
)

# 如果 MinerU 不可用，会自动回退到普通文本读取
chunks = chunker.chunk_document("your_document.pdf")
```

### MinerU 配置

```python
# 检查 MinerU 是否可用
from enhanced_text_chunker import MINERU_AVAILABLE

if MINERU_AVAILABLE:
    print("MinerU 可用")
else:
    print("MinerU 不可用，将使用回退方法")
```

## 高级用法

### 自定义章节检测

```python
chunker = EnhancedTextChunker()

# 添加自定义章节模式
chunker.chapter_patterns.append(
    (r'\n\s*自定义章节格式[^\n]*', 80)
)
```

### 处理分块结果

```python
from enhanced_text_chunker import EnhancedTextChunker
import json

chunker = EnhancedTextChunker(strategy=ChunkStrategy.HYBRID)
chunks = chunker.chunk_text(text)

# 转换为字典
chunks_dict = [chunk.to_dict() for chunk in chunks]

# 导出到 JSON
with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(chunks_dict, f, ensure_ascii=False, indent=2)

# 按章节筛选
chapter_chunks = [
    chunk for chunk in chunks
    if chunk.metadata.get('chapter_number') == 1
]

# 获取所有章节标题
titles = [
    chunk.metadata['chapter_title']
    for chunk in chunks
    if 'chapter_title' in chunk.metadata
]
```

### 与 LLM 集成

```python
from enhanced_text_chunker import EnhancedTextChunker

chunker = EnhancedTextChunker(
    strategy=ChunkStrategy.HYBRID,
    chunk_size=2000  # 根据你的 LLM 上下文窗口调整
)

chunks = chunker.chunk_text(novel_text)

# 逐块发送给 LLM
for chunk in chunks:
    prompt = f"""
    分析以下章节内容：
    标题: {chunk.metadata.get('chapter_title', '未知')}
    内容: {chunk.content}

    请总结本章的主要情节。
    """

    response = call_llm(prompt)
    # 处理响应...
```

## 配置参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `strategy` | ChunkStrategy | HYBRID | 分块策略 |
| `chunk_size` | int | 1000 | 目标分块大小（字符数） |
| `overlap` | int | 100 | 重叠窗口大小 |
| `use_mineru` | bool | True | 是否尝试使用 MinerU |
| `enable_semantic` | bool | True | 是否启用语义分析（关键词提取） |

## 输出格式

每个分块包含以下字段：

```python
{
    "id": "hybrid_0_a1b2c3d4",      # 唯一标识符
    "content": "...",              # 分块内容
    "chunk_type": "hybrid",        # 分块类型
    "metadata": {                  # 元数据
        "chapter_number": 1,       # 章节编号
        "chapter_title": "第一章", # 章节标题
        "keywords": ["关键词1", ...],  # 关键词（语义分析）
        "topic": "主题",           # 主题（语义分析）
        ...
    },
    "start_pos": 0,               # 在原文中的起始位置
    "end_pos": 500,                # 在原文中的结束位置
    "word_count": 500              # 字符数
}
```

## 性能优化

1. **大文件处理**：对于超大文件，可以先按章节检测，再逐章处理
2. **并行处理**：各章节分块可以并行进行
3. **缓存结果**：重复处理的文件可以缓存分块结果

```python
import json
from pathlib import Path

def get_cached_chunks(file_path, chunker):
    """使用缓存的分块结果"""
    cache_file = f"{file_path}.chunks.json"

    if Path(cache_file).exists():
        with open(cache_file, 'r', encoding='utf-8') as f:
            return [json.loads(line) for line in f]

    # 执行分块
    chunks = chunker.chunk_document(file_path)

    # 保存到缓存
    with open(cache_file, 'w', encoding='utf-8') as f:
        for chunk in chunks:
            f.write(json.dumps(chunk.to_dict(), ensure_ascii=False) + '\n')

    return chunks
```

## 常见问题

### Q: 如何选择合适的 chunk_size？

A: 根据你的 LLM 上下文窗口和任务需求：
- 小模型（4K 上下文）：500-800 字符
- 中等模型（8K 上下文）：1000-2000 字符
- 大模型（32K+ 上下文）：2000-4000 字符

### Q: MinerU 解析失败怎么办？

A: 系统会自动回退到普通文本读取。你也可以手动设置 `use_mineru=False`。

### Q: 章节检测不准确怎么办？

A: 可以添加自定义章节模式，或使用 SEMANTIC 策略替代。

### Q: 如何处理混合格式文件？

A: 建议使用 HYBRID 策略，它会在章节检测和语义分块之间自动平衡。

## 示例代码

查看 `examples/text_chunking_examples.py` 获取更多使用示例。

## 更新日志

- v1.0.0 - 初始版本，支持5种分块策略和MinerU集成
