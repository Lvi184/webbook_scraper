# 小说仿写系统使用指南

## 概述

本文档介绍 `app_adaptation.py` 模块的使用方法，这是一个基于拆书逻辑的小说仿写系统。

## 核心功能

### 1. 基于拆书逻辑的仿写
- 读取原始拆书结果
- 应用用户设定的改编方向
- 自动生成仿写内容
- 控制仿写章节数量和字数
- 保持原作结构和节奏

### 2. 用户友好的界面
- 交互式配置界面
- 改编要求输入
- 仿写参数设置
- 结果展示和导出

## 使用流程

### 步骤1：选择原始书籍
选择要仿写的原始书籍文件（支持PDF、DOCX、TXT格式）

### 步骤2：配置改编要求
输入你的改编要求：
- **世界观配置**：描述新的世界观设定
- **角色配置**：描述主要角色的设定
- **剧情配置**：描述剧情设定
- **文风配置**：描述期望的文风

### 步骤3：设置仿写参数
设置仿写参数：
- **章节数量**：要仿写的章节数量
- **目标字数**：每章目标字数

### 步骤4：执行仿写
系统自动执行仿写流程，生成仿写内容

### 步骤5：查看结果
查看仿写结果，可以选择保存到文件

## 系统架构

### 核心模块

1. **`services/novel_adaptation_engine.py`** - 小说仿写引擎
   - 基于拆书逻辑的自动化仿写系统
   - 支持用户自定义改编方向
   - 控制仿写章节数量和字数
   - 保持原作结构和节奏

2. **`services/adaptation_interface.py`** - 仿写界面
   - 用户友好的交互界面
   - 改编配置管理
   - 仿写过程控制
   - 结果展示和导出

3. **`app_adaptation.py`** - Streamlit界面
   - 基于 Streamlit 的 Web 界面
   - 交互式配置
   - 结果展示

### 工作流程

1. **拆解原始书籍**：使用优化版分析器拆解原始书籍
2. **应用改编配置**：将用户设定的改编方向应用到拆解结果
3. **生成仿写内容**：基于拆解结果和改编配置生成仿写内容
4. **展示结果**：在界面上展示仿写结果

## 配置选项

### 改编配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| 世界观配置 | 描述新的世界观设定 | `{"type": "赛博朋克", "power_system": "基因武学", "core_setting": "SSS级武圣"}` |
| 角色配置 | 描述主要角色的设定 | `{"萧衍": {"type": "重生武圣", "personality": "外表孱弱、眼神沧桑", "abilities": "神级洞察系统"}}` |
| 剧情配置 | 描述剧情设定 | `{"background": "重生武圣萧衍在赛博都市的底层挣扎", "conflict": "与背叛者的复仇"}` |
| 文风配置 | 描述期望的文风 | `{"type": "古龙式", "language": "语言精炼，富有诗意", "rhythm": "叙事节奏独特"}` |

### 仿写参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| 章节数量 | 要仿写的章节数量 | 3 |
| 目标字数 | 每章目标字数 | 2000 |

## 使用示例

### 示例1：基本仿写

```python
from novel_adaptation_engine import NovelAdaptationEngine, create_adaptation_config

# 创建仿写引擎
engine = NovelAdaptationEngine(llm_client=your_llm_client)

# 创建改编配置
config = create_adaptation_config(
    world_view={
        "type": "赛博朋克",
        "power_system": "基因武学",
        "core_setting": "SSS级武圣"
    },
    characters={
        "萧衍": {
            "type": "重生武圣",
            "personality": "外表孱弱、眼神沧桑",
            "abilities": "神级洞察系统"
        },
        "零": {
            "type": "孤僻少年",
            "personality": "倔强、沉默",
            "abilities": "拔刀斩"
        }
    },
    plot={
        "background": "重生武圣萧衍在赛博都市的底层挣扎",
        "conflict": "与背叛者的复仇"
    },
    style={
        "type": "古龙式",
        "language": "语言精炼，富有诗意",
        "rhythm": "叙事节奏独特"
    }
)

# 执行仿写
results = engine.adapt_novel(
    original_book_path="original_novel.txt",
    adaptation_config=config,
    chapters_to_adapt=3,
    target_word_count=2000
)

# 保存结果
with open("adapted_novel.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
```

### 示例2：交互式使用

```python
from adaptation_interface import run_adaptation_interface

# 运行仿写界面
run_adaptation_interface(llm_client=your_llm_client)
```

## 界面功能

### 1. 选择书籍
- 支持PDF、DOCX、TXT格式
- 显示当前目录下的可用文件
- 用户可以选择要仿写的书籍

### 2. 配置改编
- 世界观配置输入
- 角色配置输入
- 剧情配置输入
- 文风配置输入

### 3. 设置参数
- 章节数量设置
- 目标字数设置

### 4. 执行仿写
- 显示仿写进度
- 模拟仿写过程

### 5. 查看结果
- 显示改编配置
- 显示仿写章节
- 保存结果到文件

## 技术特点

### 1. 基于拆书逻辑
- 严格遵循「先全局总纲→再分单元拆解→最后单章细纲」的顺序
- 所有拆解内容按固定模块分类，可单独提取、替换、复用
- 100%原文贴合，不主观编造、不过度解读

### 2. 改编适配功能
- 角色/金手指替换改编
- 世界观/时代背景替换改编
- 全文仿写二次创作
- 多本融合创作

### 3. 自动化仿写
- 自动提取对应内容进行仿写
- 控制仿写章节数量和字数
- 保持原作结构和节奏

## 启动应用

```bash
# 启动仿写平台
python start_adaptation.py

# 或直接运行
streamlit run app_adaptation.py --server.port 8502
```

## 访问地址

🌐 http://localhost:8502

## 下一步计划

1. 添加更多改编模板
2. 优化LLM提示词，提高仿写准确性
3. 添加结果可视化功能
4. 支持更多文件格式
5. 添加单元测试和性能测试

## 技术支持

如遇问题，请检查：
1. LLM客户端是否正确配置
2. 文件编码是否为UTF-8
3. 日志输出中的错误信息
4. 网络连接是否正常