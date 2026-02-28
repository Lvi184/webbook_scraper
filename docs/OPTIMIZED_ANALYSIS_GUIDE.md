# 优化版书籍分析器使用指南

## 概述

本文档介绍 `optimized_book_analyzer.py` 模块的使用方法，这是一个基于全维度结构化拆书方案的增强版分析器。

## 核心特点

### 1. 严格遵循拆书流程
- **流程不可逆原则**：严格遵循「先全局总纲→再分单元拆解→最后单章细纲」的顺序
- **结构化可复用原则**：所有拆解内容按固定模块分类，可单独提取、替换、复用
- **100%原文贴合原则**：所有拆解内容完全基于原作原文，不主观编造、不过度解读
- **改编适配颗粒度原则**：拆解下沉到单章的每一个情节节点、情绪节点、人设节点

### 2. 4阶段拆书流程

#### 阶段1：前置预处理 - 全书剧情单元划分
- **拆解目标**：把全书按剧情起承转合，划分成固定的剧情单元
- **拆解要求**：严格按原作章节顺序划分，每个单元标注清楚「章节范围+单元核心主题」
- **输出**：剧情单元列表，每个单元包含章节范围、核心主题、内容

#### 阶段2：顶层宏观拆书 - 全书核心总纲拆解
- **拆解目标**：定死全书的底层规则和核心骨架
- **拆解要求**：覆盖世界观、核心大纲、角色设定3个核心模块
- **输出**：
  - 世界观核心总纲（5个核心维度）
  - 全本核心大纲（完整剧情线+核心节点）
  - 全本核心角色总设定（7个核心维度）

#### 阶段3：中层中观拆书 - 分剧情单元5维拆解
- **拆解目标**：把全书总纲落地到每个剧情段
- **拆解要求**：每个单元必须完成5个维度的拆解
- **输出**：
  - 单元大纲设计（对应参考平台「大纲设计」模块）
  - 单元世界观设计（对应参考平台「世界观设计」模块）
  - 单元人物塑造设计（对应参考平台「人物塑造设计」模块）
  - 单元情绪设计（对应参考平台「情绪设计」模块）
  - 单元角色设计校验（适配改编补充模块）

#### 阶段4：底层微观拆书 - 单章细纲全维度拆解
- **拆解目标**：把拆解下沉到每一章的每一个情节节点
- **拆解要求**：按章节顺序逐章拆解，每一章独立成块
- **输出**：
  - 本章核心定位（在全书中的作用、核心目标、核心冲突）
  - 本章剧情细纲（按情节推进顺序，精准到每个节点）
  - 本章核心创作逻辑拆解（爽点设计、节奏设计、人设塑造、世界观展现）
  - 改编适配校验（核心不可替换的剧情骨架、可替换内容、人设适配要点）

## 使用方法

### 基础使用

```python
from optimized_book_analyzer import OptimizedBookAnalyzer

# 创建优化版分析器
analyzer = OptimizedBookAnalyzer(
    llm_client=your_llm_client,
    chunking_strategy="hybrid",
    chunk_size=1000,
    use_mineru=True
)

# 执行分析
result = analyzer.analyze_book("your_novel.txt")

# 访问结果
print(f"总章节数: {result['book_info']['total_chapters']}")
print(f"总单元数: {result['book_info']['total_units']}")

# 查看单元划分
for unit in result['stage1_units']:
    print(f"单元 {unit['unit_number']}: {unit['chapter_range']} - {unit['theme']}")

# 查看宏观分析
print("\n世界观总纲:")
print(result['stage2_world_outline'])

# 查看单元分析
for unit_analysis in result['stage3_units_analysis']:
    print(f"\n单元 {unit_analysis['unit_number']} 分析:")
    print(f"大纲设计: {unit_analysis['单元大纲设计'][:100]}...")
    print(f"情绪设计: {unit_analysis['单元情绪设计'][:100]}...")

# 查看章节分析
for chapter_analysis in result['stage4_chapters_analysis']:
    print(f"\n第{chapter_analysis['chapter_number']}章:")
    print(f"核心定位: {chapter_analysis['本章核心定位']}")
    print(f"剧情细纲: {chapter_analysis['本章剧情细纲'][:100]}...")
```

### 便捷函数

```python
from optimized_book_analyzer import optimized_analyze_book_file

# 一行代码完成分析
result = optimized_analyze_book_file(
    "your_novel.txt",
    llm_client=your_llm_client,
    chunking_strategy="hybrid",
    chunk_size=1000
)
```

## 改编适配功能

### 1. 角色/金手指替换改编
- **对标模板**：《全本核心角色总设定拆解》+ 分单元人物塑造设计 + 单章人设塑造拆解
- **操作方法**：
  1. 确定要替换的原作角色，对标其核心功能、剧情定位、成长线
  2. 设计新角色的人设、金手指、背景
  3. 调整新角色的对应行动，保证新人设完全适配原作的剧情骨架

### 2. 世界观/时代背景替换改编
- **对标模板**：《全书世界观核心总纲》+ 分单元世界观设计 + 单章世界观展现拆解
- **操作方法**：
  1. 对标原作的世界观核心逻辑，设计新的世界观、时代背景、力量体系
  2. 把原作的武侠江湖设定，对应替换成新的世界观设定
  3. 保证新世界观的规则完全适配原作的剧情冲突、爽点设计

### 3. 全文仿写二次创作
- **对标模板**：全本所有拆书成果，从总纲到单章细纲
- **操作方法**：
  1. 完成角色、世界观的替换设计，确定改编后的核心设定
  2. 对标《全本核心大纲》，生成改编后的全本大纲
  3. 对标分剧情单元的5维拆解，生成改编后的分单元剧情
  4. 对标《单章细纲拆解》，逐章仿写正文内容

### 4. 多本融合创作
- **对标模板**：拆书成果库
- **操作方法**：把多本书的拆书成果融合，生成全新的故事大纲和内容

## 配置选项

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `chunking_strategy` | str | "hybrid" | 分块策略 (chapter/semantic/fixed_size/adaptive/hybrid) |
| `chunk_size` | int | 1000 | 分块大小 |
| `use_mineru` | bool | False | 是否使用MinerU进行高质量文档解析 |
| `unit_size` | int | 5 | 剧情单元包含的章节数 |

## 输出格式

### 阶段1：前置预处理
```json
{
  "units": [
    {
      "unit_number": 1,
      "chapter_range": "第1-5章",
      "theme": "少年得志与成长",
      "chapters": [...],
      "content": "...",
      "word_count": 5000
    }
  ]
}
```

### 阶段2：顶层宏观拆书
```json
{
  "stage2_world_outline": "世界观核心总纲内容...",
  "stage2_main_outline": "全本核心大纲内容...",
  "stage2_characters": "全本核心角色总设定内容..."
}
```

### 阶段3：中层中观拆书
```json
{
  "stage3_units_analysis": [
    {
      "unit_number": 1,
      "unit_info": {
        "chapter_range": "第1-5章",
        "theme": "少年得志与成长",
        "word_count": 5000
      },
      "单元大纲设计": "...",
      "单元世界观设计": "...",
      "单元人物塑造设计": "...",
      "单元情绪设计": "...",
      "单元角色设计校验": "..."
    }
  ]
}
```

### 阶段4：底层微观拆书
```json
{
  "stage4_chapters_analysis": [
    {
      "chapter_number": 1,
      "chapter_title": "第一章 少年得志",
      "word_count": 1000,
      "本章核心定位": "...",
      "本章剧情细纲": "...",
      "本章核心创作逻辑拆解": "...",
      "改编适配校验": "..."
    }
  ]
}
```

## 性能优化建议

1. **大文件处理**：对于超大文件，可以先按章节检测，再逐章处理
2. **并行处理**：各单元分析可以并行进行
3. **缓存结果**：重复处理的文件可以缓存拆书结果
4. **LLM优化**：使用批量处理减少API调用次数

## 常见问题

### Q1: 如何选择合适的 unit_size？

A: 根据原作节奏调整：
- 短篇/节奏快的作品：3-4章/单元
- 中篇/节奏适中的作品：5章/单元（推荐）
- 长篇/节奏慢的作品：6-8章/单元

### Q2: 改编时如何保证人设不OOC？

A: 使用「单元角色设计校验」和「改编适配校验」模块：
- 检查新角色的行为是否符合原作核心人设
- 确保关键情节节点的人设一致性
- 参考原作在相似场景下的角色表现

### Q3: 如何处理没有章节划分的文本？

A: 使用自适应分块策略：
```python
analyzer = OptimizedBookAnalyzer(
    llm_client=your_llm_client,
    chunking_strategy="adaptive",  # 自适应策略
    chunk_size=1000
)
```

## 示例代码位置

- 基础示例：`examples/optimized_text_chunking_examples.py`
- 详细指南：`docs/OPTIMIZED_ANALYSIS_GUIDE.md`
- 核心模块：`services/optimized_book_analyzer.py`

## 下一步

1. 运行示例：`python examples/optimized_text_chunking_examples.py`
2. 集成到现有项目
3. 测试分析结果
4. 优化LLM提示词

## 技术支持

如遇问题，请检查：
1. LLM客户端是否正确配置
2. 文件编码是否为UTF-8
3. 日志输出中的错误信息
4. 单元大小是否适合原作节奏