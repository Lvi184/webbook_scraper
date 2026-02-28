import streamlit as st
import os
import json
from pathlib import Path
from datetime import datetime

# 导入自定义服务
from services.file_parser import FileParser
from services.text_processor import TextProcessor
from services.book_analyzer import BookAnalyzer
from services.llm_client import LLMClient
from config_loader import ConfigLoader

# 页面配置
st.set_page_config(
    page_title="全维度网文拆书平台",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化session state
if 'processing_status' not in st.session_state:
    st.session_state.processing_status = "idle"
if 'current_file' not in st.session_state:
    st.session_state.current_file = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# 页面导航
pages = {
    "主界面": "main",
    "模型管理": "model_manager",
    "本地配置": "local_config"
}

# 选择页面
selected_page = st.sidebar.selectbox(
    "导航",
    list(pages.keys()),
    index=0
)

# 如果选择其他页面，显示相应内容
if selected_page != "主界面":
    if selected_page == "模型管理":
        import app_model_manager
        app_model_manager.model_manager()
    elif selected_page == "本地配置":
        import app_local_config
        app_local_config.local_config()
    st.stop()

def save_uploaded_file(uploaded_file) -> str:
    """保存上传的文件"""
    upload_dir = Path("data/uploads")
    upload_dir.mkdir(exist_ok=True)

    # 安全处理文件名，移除或替换特殊字符
    safe_filename = uploaded_file.name.replace(' ', '_').replace('\u3000', '_')
    file_path = upload_dir / safe_filename
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return str(file_path)

def display_analysis_results(result: dict):
    """分析结果展示"""
    st.success("✅ 拆书分析完成！")

    # 创建标签页展示不同阶段结果
    tabs = st.tabs(["📊 总览", "🌍 世界观总纲", "🎭 角色设定", "📖 剧情单元", "📝 单章细纲"])

    with tabs[0]:  # 总览
        st.subheader("📊 书籍信息")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**文件名**: {result['book_info']['filename']}")
            st.write(f"**总章节数**: {result['book_info']['total_chapters']}")
            st.write(f"**剧情单元数**: {result['book_info']['total_units']}")

        with col2:
            st.metric("分析进度", "100%")

        st.subheader("📋 各阶段成果")
        stage_info = {
            "阶段1 - 剧情单元划分": f"{result['book_info']['total_units']}个单元",
            "阶段2 - 顶层宏观拆书": f"世界观+大纲+角色{len(result['stage2_characters'])}个",
            "阶段3 - 中观单元分析": f"{len(result['stage3_units_analysis'])}个单元5维分析",
            "阶段4 - 微观细纲拆解": f"{len(result['stage4_chapters_analysis'])}章细纲"
        }

        for stage, info in stage_info.items():
            st.write(f"- **{stage}**: {info}")

    with tabs[1]:  # 世界观总纲
        st.subheader("🌍 全书世界观核心总纲")
        world_outline = result['stage2_world_outline']

        if isinstance(world_outline, dict):
            st.json(world_outline)
        else:
            st.text(world_outline)

    with tabs[2]:  # 角色设定
        st.subheader("🎭 全本核心角色总设定")
        characters = result['stage2_characters']

        if isinstance(characters, list):
            for i, char in enumerate(characters):
                st.write(f"### 角色{i+1}")
                if isinstance(char, dict):
                    st.json(char)
                else:
                    st.text(char)
                st.write("---")
        else:
            st.text(characters)

    with tabs[3]:  # 剧情单元
        st.subheader("📖 分剧情单元5维拆解")
        units = result['stage3_units_analysis']

        # 单元选择器
        unit_numbers = [f"单元{unit['unit_number']}" for unit in units]
        selected_unit = st.selectbox("选择单元", unit_numbers)

        if selected_unit:
            unit_idx = int(selected_unit.replace("单元", "")) - 1
            unit_data = units[unit_idx]

            st.write(f"**单元范围**: 第{unit_data['chapter_range'][0]}-{unit_data['chapter_range'][-1]}章")
            st.write(f"**单元主题**: {unit_data['theme']}")

            # 5维分析结果
            dimensions = ['单元大纲设计', '单元世界观设计', '单元人物塑造设计', '单元情绪设计', '单元角色设计校验']
            selected_dim = st.selectbox("选择维度", dimensions)

            st.write(f"### {selected_dim}")
            if selected_dim in unit_data:
                st.json(unit_data[selected_dim])

    with tabs[4]:  # 单章细纲
        st.subheader("📝 单章细纲全维度拆解")
        chapters = result['stage4_chapters_analysis']

        # 章节选择器
        chapter_options = [f"第{ch['chapter_number']}章 {ch['title']}" for ch in chapters]
        selected_chapter = st.selectbox("选择章节", chapter_options)

        if selected_chapter:
            chapter_idx = int(selected_chapter.split()[0].replace("第", "").replace("章", "")) - 1
            chapter_data = chapters[chapter_idx]

            st.write(f"### 第{chapter_data['chapter_number']}章 {chapter_data['title']}")

            # 4个维度展示
            dims = ['本章核心定位', '本章剧情细纲', '本章核心创作逻辑拆解', '改编适配校验']
            for dim in dims:
                st.write(f"#### {dim}")
                if dim in chapter_data:
                    st.json(chapter_data[dim])

    # 下载结果按钮
    json_str = json.dumps(result, ensure_ascii=False, indent=2)
    st.download_button(
        label="📥 下载完整分析结果 (JSON)",
        data=json_str,
        file_name=f"book_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

def main():
    """主函数"""
    st.title("📚 全维度结构化网文拆书平台")
    st.markdown("专为网文仿写改编设计的智能拆书系统")

    # 加载配置
    config_loader = ConfigLoader()

    # 侧边栏
    with st.sidebar:
        st.header("⚙️ 模型配置")

        # API Key输入
        api_key = st.text_input(
            "API Key",
            type="password",
            help="请输入您的API密钥"
        )

        # 提供商选择
        providers = config_loader.get_providers()
        selected_provider = st.selectbox(
            "选择提供商",
            providers,
            index=0,
            help="选择要使用的AI模型提供商"
        )

        # 获取当前提供商的模型
        models = config_loader.get_models_by_provider(selected_provider)

        if selected_provider == "local":
            # 对于本地模型，动态获取可用模型
            try:
                temp_client = LLMClient("", "local")
                model_options = temp_client.get_models_for_provider("local")
            except:
                model_options = ["llama2", "qwen-7b"]
        else:
            model_options = list(models.keys())

        # 模型选择
        selected_model = st.selectbox(
            "选择模型",
            model_options,
            index=0,
            help="选择具体使用的模型"
        )

        # 显示模型描述（对于非本地模型）
        if selected_provider != "local" and selected_model in models:
            model_info = models[selected_model]
            st.info(f"**{model_info['name']}**")
            st.caption(model_info['description'])
            st.write(f"最大Token数: {model_info['max_tokens']}")
            st.write(f"提供商: {model_info['provider']}")
        elif selected_provider == "local":
            st.info(f"**本地模型: {selected_model}**")
            st.caption("运行在本地服务器上的模型")
            st.write("提供商: 本地部署")
            st.write("最大Token数: 2048 (默认)")
        else:
            st.warning("模型信息不可用")

        st.markdown("---")
        st.markdown("### 📋 使用说明")
        st.markdown("1. 上传网文文件（PDF/DOCX/TXT）")
        st.markdown("2. 等待自动分析完成")
        st.markdown("3. 查看各阶段拆书结果")
        st.markdown("4. 下载分析结果")

    # 主界面
    if st.session_state.processing_status == "idle":
        # 文件上传区域
        st.subheader("📁 上传网文文件")
        uploaded_file = st.file_uploader(
            "选择文件",
            type=['pdf', 'docx', 'txt'],
            help="支持PDF、DOCX、TXT格式，建议文件大小不超过10MB"
        )

        if uploaded_file is not None:
            # 显示文件信息
            with st.expander("📄 文件信息"):
                st.write(f"**文件名**: {uploaded_file.name}")
                st.write(f"**文件大小**: {uploaded_file.size / 1024 / 1024:.2f} MB")
                st.write(f"**文件类型**: {uploaded_file.name.split('.')[-1].upper()}")

            # 开始分析按钮
            if st.button("🚀 开始拆书分析", type="primary"):
                if not api_key:
                    st.error("❌ 请先在侧边栏输入OpenAI API Key")
                    return

                try:
                    # 保存文件
                    file_path = save_uploaded_file(uploaded_file)
                    st.session_state.current_file = file_path

                    # 初始化服务
                    with st.spinner("正在初始化服务..."):
                        llm_client = LLMClient(api_key, selected_provider, selected_model)
                        file_parser = FileParser()
                        text_processor = TextProcessor()
                        analyzer = BookAnalyzer(llm_client)

                    # 解析文件
                    with st.spinner("正在解析文件..."):
                        file_data = file_parser.parse_file(file_path)

                    # 显示文件解析结果
                    st.success("✅ 文件解析完成！")
                    st.write(f"**检测到章节**: {file_data['total_chapters']}章")

                    # 显示前5个章节标题
                    with st.expander("📖 章节预览"):
                        for i, chapter in enumerate(file_data['chapters'][:5]):
                            st.write(f"**第{i+1}章**: {chapter['title']}")
                        if len(file_data['chapters']) > 5:
                            st.write(f"...还有{len(file_data['chapters'])-5}个章节")

                    # 开始分析
                    st.session_state.processing_status = "processing"
                    st.progress(0)
                    st.info("🔄 开始四阶段拆书分析...")

                    # 执行分析
                    with st.spinner("正在进行四阶段拆书分析..."):
                        result = analyzer.analyze_book(file_data)
                        st.session_state.analysis_result = result

                    st.session_state.processing_status = "completed"

                    # 显示结果
                    display_analysis_results(result)

                except Exception as e:
                    st.error(f"❌ 分析失败: {str(e)}")
                    st.session_state.processing_status = "idle"

    elif st.session_state.processing_status == "processing":
        st.info("🔄 正在分析中，请稍候...")
        st.progress(0.5)

    elif st.session_state.processing_status == "completed":
        # 显示结果
        if st.session_state.analysis_result:
            display_analysis_results(st.session_state.analysis_result)

        # 重新分析按钮
        if st.button("🔄 重新分析"):
            st.session_state.processing_status = "idle"
            st.rerun()

if __name__ == "__main__":
    main()