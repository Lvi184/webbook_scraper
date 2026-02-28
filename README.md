# 全维度网文拆书平台

一个基于Python的本地化网文拆书工具，专门用于分析网文结构，支持仿写改编。

## 功能特点

- 📚 **多格式支持**：支持PDF、DOCX、TXT格式
- 🔄 **四阶段拆书**：
  1. 前置预处理 - 剧情单元划分
  2. 顶层宏观拆书 - 世界观总纲+核心大纲+角色设定
  3. 中层中观拆书 - 单元5维分析
  4. 底层微观拆书 - 单章细纲拆解
- 🎯 **智能分块**：自动识别中文章节，按语义分块
- 📊 **可视化界面**：基于Streamlit的友好界面
- 💾 **结果导出**：支持JSON格式导出完整分析

## 快速开始

### 1. 安装依赖

```bash
pip install streamlit pdfplumber python-docx jieba openai
```

### 2. 运行应用

```bash
streamlit run app.py
```

### 3. 使用步骤

1. 在侧边栏输入OpenAI API Key
2. 上传网文文件（PDF/DOCX/TXT）
3. 点击"开始拆书分析"
4. 等待分析完成
5. 在不同标签页查看分析结果
6. 下载完整分析结果

## 目录结构

```
webbook_scraper/
├── app.py                 # 主应用界面
├── init.py               # 初始化脚本
├── config.json           # 配置文件
├── requirements.txt      # 依赖列表
├── README.md             # 说明文档
├── data/                 # 数据目录
│   ├── uploads/          # 上传文件
│   └── results/          # 分析结果
├── services/             # 服务模块
│   ├── file_parser.py    # 文件解析
│   ├── text_processor.py # 文本处理
│   ├── book_analyzer.py  # 拆书分析
│   └── llm_client.py     # LLM客户端
└── templates/            # 模板目录
```

## 配置说明

在`config.json`中可以配置以下参数：

- `model`: 使用的OpenAI模型（默认：gpt-3.5-turbo）
- `chunk_size`: 文本分块大小（默认：1000）
- `unit_size`: 剧情单元包含章节数（默认：5）
- `max_tokens`: LLM最大输出token数（默认：2000）
- `temperature`: LLM温度参数（默认：0.7）

## 注意事项

1. 需要有效的OpenAI API Key
2. 建议单次处理文件不超过10MB
3. 分析过程可能需要几分钟时间
4. 结果会自动保存到本地

## 常见问题

### Q: 如何获取OpenAI API Key？
A: 访问 https://platform.openai.com/ 注册账号并创建API Key。

### Q: 支持哪些文件格式？
A: 目前支持PDF、DOCX和TXT格式。

### Q: 分析结果在哪里查看？
A: 分析完成后会在界面上以标签页形式展示，也可以下载JSON文件。

### Q: 可以离线使用吗？
A: 文件处理和界面完全本地化，但需要联网调用OpenAI API。