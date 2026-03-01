"""
整合系统 - 拆书与仿写一体化平台
"""

import streamlit as st
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# 导入现有服务
from services.file_parser import FileParser
from services.text_processor import TextProcessor
from services.book_analyzer import BookAnalyzer
from services.llm_client import LLMClient
from services.novel_adaptation_engine import NovelAdaptationEngine
from services.unified_pipeline_service import UnifiedPipelineService
from config_loader import ConfigLoader

# 页面配置
st.set_page_config(
    page_title="拆书仿写一体化平台",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化session state
if 'processing_pipeline' not in st.session_state:
    st.session_state.processing_pipeline = {
        'step': 'start',
        'current_file': None,
        'analysis_result': None,
        'adaptation_config': None,
        'adaptation_results': None,
        'full_results': None
    }

# 页面导航
pipeline_steps = [
    "🏁 开始",
    "📚 拆书分析",
    "🎨 仿写配置",
    "✍️ 执行仿写",
    "📊 结果展示"
]

# 侧边栏 - 流程控制
with st.sidebar:
    st.header("🔄 处理流程")

    # 显示当前步骤
    current_step_index = pipeline_steps.index(st.session_state.processing_pipeline['step'])
    for i, step in enumerate(pipeline_steps):
        if i < current_step_index:
            st.markdown(f"✅ {step}")
        elif i == current_step_index:
            st.markdown(f"🟡 **{step}**")
        else:
            st.markdown(f"⚪ {step}")

    # 重置按钮
    if st.button("重置流程"):
        st.session_state.processing_pipeline = {
            'step': 'start',
            'current_file': None,
            'analysis_result': None,
            'adaptation_config': None,
            'adaptation_results': None,
            'full_results': None
        }
        st.rerun()

def save_uploaded_file(uploaded_file) -> str:
    """保存上传的文件"""
    import os
    upload_dir = os.path.join(os.getcwd(), "data", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return file_path

def display_analysis_preview(analysis_result: Dict):
    """显示拆书分析预览"""
    book_info = analysis_result.get('book_info', {})

    st.subheader("📊 分析结果预览")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("章节数", book_info.get('total_chapters', 0))
    with col2:
        st.metric("剧情单元", book_info.get('total_units', 0))
    with col3:
        st.metric("核心角色", len(analysis_result.get('stage2_characters', [])))

    # 显示世界观总纲
    if 'stage2_world_outline' in analysis_result:
        st.write("**世界观总纲**")
        world_outline = analysis_result['stage2_world_outline']
        st.write(f"- 时空背景: {world_outline.get('基础时空背景', '未知')}")
        st.write(f"- 核心力量体系: {json.dumps(world_outline.get('核心力量体系', {}), ensure_ascii=False)[:200]}...")

    # 显示角色设定
    if 'stage2_characters' in analysis_result and analysis_result['stage2_characters']:
        st.write("**核心角色**")
        for i, char in enumerate(analysis_result['stage2_characters'][:3]):
            if isinstance(char, dict) and 'name' in char:
                st.write(f"- {char.get('name', '未知')}: {char.get('description', '未知')[:100]}...")

def display_analysis_results(analysis_result: Dict):
    """显示完整的拆书分析结果"""
    # 创建标签页显示各个阶段
    stages = [
        ("📊 基本信息", "basic_info"),
        ("🌍 世界观分析", "world_view"),
        ("👥 角色分析", "characters"),
        ("📖 剧情分析", "plot"),
        ("🎭 单元分析", "units"),
        ("📝 章节分析", "chapters")
    ]

    tabs = st.tabs([name for name, _ in stages])

    for tab, (name, stage_key) in zip(tabs, stages):
        with tab:
            if stage_key == "basic_info":
                book_info = analysis_result.get('book_info', {})
                st.write(f"**文件名**: {book_info.get('filename', '未知')}")
                st.write(f"**章节数**: {book_info.get('total_chapters', 0)}")
                st.write(f"**剧情单元**: {book_info.get('total_units', 0)}")

            elif stage_key == "world_view" and 'stage2_world_outline' in analysis_result:
                world_outline = analysis_result['stage2_world_outline']
                st.json(world_outline)

            elif stage_key == "characters" and 'stage2_characters' in analysis_result:
                st.json(analysis_result['stage2_characters'])

            elif stage_key == "plot" and 'stage2_main_plot' in analysis_result:
                st.json(analysis_result['stage2_main_plot'])

            elif stage_key == "units" and 'stage3_units_analysis' in analysis_result:
                st.write("### 单元分析")
                for unit_analysis in analysis_result['stage3_units_analysis'][:5]:
                    st.write(f"**单元 {unit_analysis.get('unit_number', 0)}**")
                    st.json(unit_analysis)

            elif stage_key == "chapters" and 'stage4_chapters_analysis' in analysis_result:
                st.write("### 章节分析")
                for chapter_analysis in analysis_result['stage4_chapters_analysis'][:10]:
                    st.write(f"**第{chapter_analysis.get('chapter_number', 0)}章**")
                    st.write(f"- 标题: {chapter_analysis.get('title', '未知')}")
                    if '本章剧情细纲' in chapter_analysis:
                        st.write("- 剧情细纲:")
                        st.json(chapter_analysis['本章剧情细纲'])

def show_start_step():
    """步骤1: 开始界面"""
    st.header("🏁 欢迎使用拆书仿写一体化平台")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📚 系统功能")
        st.markdown("""
        - **四阶段拆书分析**：深度解析小说结构
        - **智能仿写创作**：基于拆书结果进行创作
        - **多样化创作模式**：忠实仿写、创意改写、平行世界等
        - **完整流程管理**：从分析到创作的无缝衔接
        """)

    with col2:
        st.subheader("🎯 使用流程")
        st.markdown("""
        1. **上传书籍** - 支持TXT、PDF、DOCX格式
        2. **执行拆书** - 自动进行四阶段分析
        3. **配置仿写** - 选择创作模式和参数
        4. **生成仿写** - 基于拆书结果创作新内容
        5. **查看结果** - 展示完整分析+仿写成果
        """)

    st.divider()

    # 文件上传
    st.subheader("📁 选择书籍文件")
    uploaded_file = st.file_uploader(
        "上传要分析的书籍文件",
        type=['txt', 'pdf', 'docx'],
        help="支持 TXT、PDF、DOCX 格式，建议文件大小不超过10MB"
    )

    # 下一步按钮
    if uploaded_file:
        if st.button("🚀 开始拆书分析", type="primary"):
            # 保存文件
            file_path = save_uploaded_file(uploaded_file)
            st.session_state.processing_pipeline['current_file'] = file_path
            st.session_state.processing_pipeline['step'] = 'analysis'
            st.rerun()
    else:
        st.info("请上传书籍文件以开始分析")

def show_analysis_step():
    """步骤2: 拆书分析"""
    st.header("📚 拆书分析阶段")

    # 显示当前文件信息
    current_file = st.session_state.processing_pipeline['current_file']
    if current_file:
        st.info(f"正在分析文件: {Path(current_file).name}")

    # 执行拆书分析
    if st.button("🔍 开始分析", type="primary"):
        try:
            # 加载配置
            config = ConfigLoader.load_config()
            llm_client = LLMClient(config)

            # 解析文件
            file_parser = FileParser()
            file_data = file_parser.parse_file(current_file)

            # 执行分析
            from services.book_analyzer import BookAnalyzer
            book_analyzer = BookAnalyzer(llm_client)

            # 这里可以显示分析进度
            with st.spinner("正在进行四阶段拆书分析..."):
                analysis_result = book_analyzer.analyze_book(file_data)

                # 保存结果
                st.session_state.processing_pipeline['analysis_result'] = analysis_result
                st.session_state.processing_pipeline['step'] = 'adaptation_config'

                st.success("✅ 拆书分析完成！")
                st.rerun()

        except Exception as e:
            st.error(f"分析失败: {str(e)}")

    # 如果已有分析结果，显示预览
    if 'analysis_result' in st.session_state and st.session_state.analysis_result:
        st.info("💡 拆书分析已完成，您可以点击「下一步」配置仿写参数")
        display_analysis_preview(st.session_state.analysis_result)

def show_adaptation_config_step():
    """步骤3: 仿写配置"""
    st.header("🎨 仿写配置阶段")

    if not st.session_state.analysis_result:
        st.error("请先完成拆书分析")
        return

    # 显示拆书结果摘要
    st.info("📊 拆书结果摘要")
    book_info = st.session_state.analysis_result.get('book_info', {})
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("章节数", book_info.get('total_chapters', 0))
    with col2:
        st.metric("剧情单元", book_info.get('total_units', 0))
    with col3:
        st.metric("角色数量", len(st.session_state.analysis_result.get('stage2_characters', [])))

    # 仿写配置表单
    with st.form("adaptation_config_form"):
        st.subheader("📝 仿写配置")

        # 创作模式选择
        st.write("**创作模式**")
        mode = st.selectbox(
            "选择创作模式",
            options=['faithful', 'creative', 'parallel', 'prequel', 'sequel'],
            format_func=lambda x: {
                'faithful': '忠实仿写',
                'creative': '创意改写',
                'parallel': '平行世界',
                'prequel': '前传故事',
                'sequel': '续集故事'
            }[x]
        )

        # 目标参数
        col1, col2 = st.columns(2)
        with col1:
            target_chapters = st.number_input(
                "目标章节数",
                min_value=1,
                max_value=50,
                value=min(10, book_info.get('total_chapters', 10))
            )
        with col2:
            target_words = st.number_input(
                "目标总字数",
                min_value=1000,
                max_value=200000,
                value=50000,
                step=1000
            )

        # 个性化设置
        st.write("**个性化设置**")
        style = st.text_input("仿写风格", value="保持原风格")
        originality = st.slider("原创度", 0, 100, 50)

        # 配置摘要
        config_summary = {
            'mode': mode,
            'target_chapters': target_chapters,
            'target_words': target_words,
            'style': style,
            'originality': originality
        }

        st.write("**配置摘要**")
        st.json(config_summary)

        # 提交按钮
        submitted = st.form_submit_button("✍️ 开始仿写", type="primary")

        if submitted:
            st.session_state.processing_pipeline['adaptation_config'] = config_summary
            st.session_state.processing_pipeline['step'] = 'execution'
            st.rerun()

def show_execution_step():
    """步骤4: 执行仿写"""
    st.header("✍️ 执行仿写创作")

    if not st.session_state.analysis_result:
        st.error("请先完成拆书分析")
        return

    if not st.session_state.adaptation_config:
        st.error("请先配置仿写参数")
        return

    # 执行仿写
    if st.button("🚀 开始仿写", type="primary"):
        try:
            # 加载配置
            config = ConfigLoader.load_config()
            llm_client = LLMClient(config)

            # 获取分析结果
            file_data = {
                'filename': Path(st.session_state.processing_pipeline['current_file']).name,
                'chapters': st.session_state.analysis_result['stage1_units']
            }

            # 执行完整流水线
            pipeline_service = UnifiedPipelineService(llm_client)

            with st.spinner("正在进行仿写创作..."):
                full_result = pipeline_service.run_full_pipeline(
                    file_data=file_data,
                    adaptation_config=st.session_state.adaptation_config
                )

                # 保存结果
                st.session_state.processing_pipeline['full_results'] = full_result
                st.session_state.processing_pipeline['step'] = 'results'

                st.success("✅ 仿写创作完成！")
                st.rerun()

        except Exception as e:
            st.error(f"仿写失败: {str(e)}")

    # 显示配置信息
    st.info("📋 当前仿写配置")
    st.json(st.session_state.adaptation_config)

def show_results_step():
    """步骤5: 结果展示"""
    st.header("📊 完整结果展示")

    if not st.session_state.processing_pipeline.get('full_results'):
        st.error("未找到仿写结果")
        return

    full_results = st.session_state.processing_pipeline['full_results']
    data = full_results['data']

    # 创建标签页
    tabs = st.tabs([
        "📊 总览",
        "🔍 拆书分析",
        "✍️ 仿写作品",
        "📈 对比分析"
    ])

    with tabs[0]:  # 总览
        st.subheader("📊 项目总览")

        # 显示元数据
        metadata = data.get('metadata', {})
        col1, col2 = st.columns(2)
        with col1:
            st.write("**项目信息**")
            st.write(f"- 创建时间: {metadata.get('created_at', '未知')}")
            st.write(f"- 源文件: {metadata.get('source_file', '未知')}")
        with col2:
            st.write("**统计信息**")
            summary = data.get('summary', {})
            st.write(f"- 原始章节数: {summary.get('original_chapters', 0)}")
            st.write(f"- 仿写章节数: {summary.get('adapted_chapters', 0)}")
            st.write(f"- 总字数: {summary.get('total_words', 0)}")

        # 下载按钮
        st.download_button(
            label="📥 下载完整结果",
            data=json.dumps(data, ensure_ascii=False, indent=2),
            file_name=f"unified_result_{metadata.get('created_at', '').split('T')[0]}.json",
            mime="application/json"
        )

    with tabs[1]:  # 拆书分析
        st.subheader("🔍 拆书分析结果")
        display_analysis_results(data['analysis'])

    with tabs[2]:  # 仿写作品
        st.subheader("✍️ 仿写作品")
        adaptation = data.get('adaptation', {})

        # 显示仿写配置
        st.info("**仿写配置**")
        st.json(adaptation.get('config', {}))

        # 显示仿写内容
        content = adaptation.get('adapted_content', [])
        if content:
            st.write(f"**仿写章节**（共{len(content)}章）")

            # 章节选择器
            selected_chapter = st.selectbox(
                "选择要查看的章节",
                options=[f"第{c['chapter_number']}章: {c['title']}" for c in content],
                index=0
            )

            # 显示选中的章节
            chapter_num = int(selected_chapter.split('第')[1].split('章')[0]) - 1
            chapter = content[chapter_num]

            st.write(f"## {chapter['title']}")
            st.markdown(chapter['content'])
            st.caption(f"字数: {chapter['word_count']}")

    with tabs[3]:  # 对比分析
        st.subheader("📈 对比分析")

        # 世界观对比
        st.write("**世界观传承**")
        world_inspired = data.get('adaptation', {}).get('world_inspired', {})
        st.write("核心概念:")
        st.write(world_inspired.get('core_concepts', []))

        # 角色对比
        st.write("**角色关系**")
        char_inspired = data.get('adaptation', {}).get('character_inspired', [])
        for char in char_inspired[:5]:
            st.write(f"- {char['name']}: {char.get('type', '')} - {char.get('personality', '')}")

        # 剧情结构
        st.write("**剧情结构**")
        plot_inspired = data.get('adaptation', {}).get('plot_inspired', {})
        st.write(plot_inspired.get('core_summary', ''))

        # 质量评估
        st.write("**质量评估**")
        quality = data.get('adaptation', {}).get('quality_metrics', {})
        col1, col2 = st.columns(2)
        with col1:
            st.metric("章节数量", quality.get('total_chapters', 0))
            st.metric("总字数", quality.get('total_words', 0))
        with col2:
            st.metric("平均字数", quality.get('average_words_per_chapter', 0))
            st.write(f"状态: {quality.get('completeness', '未知')}")

def show_progress_bar():
    """显示进度条"""
    current_step = st.session_state.processing_pipeline['step']
    steps = ['start', 'analysis', 'adaptation_config', 'execution', 'results']

    progress = steps.index(current_step) / len(steps)

    st.progress(progress, text=f"流程进度: {progress*100:.0f}%")

# 主界面函数
def main_interface():
    """主界面 - 整合系统"""
    st.title("🔮 拆书仿写一体化平台")
    st.markdown("---")

    # 获取当前步骤
    current_step = st.session_state.processing_pipeline['step']

    # 根据步骤显示不同内容
    if current_step == 'start':
        show_start_step()
    elif current_step == 'analysis':
        show_analysis_step()
    elif current_step == 'adaptation_config':
        show_adaptation_config_step()
    elif current_step == 'execution':
        show_execution_step()
    elif current_step == 'results':
        show_results_step()

    # 进度显示
    show_progress_bar()

if __name__ == "__main__":
    main_interface()