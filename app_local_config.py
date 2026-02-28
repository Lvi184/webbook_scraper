import streamlit as st
import requests
import json
from config_loader import ConfigLoader

def local_config():
    """本地模型配置界面"""
    st.title("⚙️ 本地模型配置")
    st.markdown("配置本地部署的AI模型（如Ollama）")

    # 测试本地连接
    st.subheader("测试本地模型服务")

    if st.button("检测本地服务"):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                st.success(f"✅ 找到本地服务，可用模型: {[m['name'] for m in models]}")
            else:
                st.error("❌ 无法连接到本地服务")
        except:
            st.error("❌ 本地服务未启动或不可访问")

    # 配置本地模型
    st.subheader("添加本地模型")

    with st.form("local_model_form"):
        col1, col2 = st.columns(2)

        with col1:
            model_name = st.text_input(
                "模型名称",
                placeholder="例如: llama2",
                help="模型的内部名称"
            )

            display_name = st.text_input(
                "显示名称",
                placeholder="例如: Llama2 7B",
                help="在界面中显示的名称"
            )

        with col2:
            model_description = st.text_area(
                "模型描述",
                placeholder="描述模型的特点",
                help="模型的详细描述"
            )

        max_tokens = st.number_input(
            "最大Token数",
            min_value=100,
            max_value=8192,
            value=2048,
            help="模型支持的最大token数"
        )

        submitted = st.form_submit_button("添加本地模型")

        if submitted:
            if not all([model_name, display_name, model_description]):
                st.error("请填写所有字段")
            else:
                # 加载配置
                config_loader = ConfigLoader()

                # 添加本地模型
                if "local" not in config_loader.config["models"]:
                    config_loader.config["models"]["local"] = {}

                config_loader.config["models"]["local"][model_name] = {
                    "name": display_name,
                    "provider": "local",
                    "max_tokens": max_tokens,
                    "temperature": 0.8,
                    "description": model_description
                }

                # 保存配置
                config_loader.save_config(config_loader.config)
                st.success(f"成功添加本地模型: {display_name}")

    # 使用说明
    st.subheader("使用说明")

    st.markdown("""
    ## 安装Ollama

    1. 下载并安装Ollama: [https://ollama.com/](https://ollama.com/)
    2. 启动Ollama服务
    3. 下载模型:
       ```bash
       ollama pull llama2
       ollama pull qwen:7b
       ```

    ## 常用模型

    - **llama2**: Meta的Llama 2模型
    - **qwen:7b**: 阿里通义千问
    - **mistral**: Mistral AI模型
    - **codellama**: 代码专用模型

    ## API端点配置

    默认使用 `http://localhost:11434`，如需修改，请编辑代码中的默认值。
    """)

if __name__ == "__main__":
    local_config()