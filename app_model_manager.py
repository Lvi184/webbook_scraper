import streamlit as st
import json
from pathlib import Path
from config_loader import ConfigLoader

def model_manager():
    """模型管理界面"""
    st.title("🔧 模型管理")
    st.markdown("配置和管理可用的AI模型")

    # 加载配置
    config_loader = ConfigLoader()

    # 显示当前配置
    st.subheader("当前模型配置")
    st.json(config_loader.config["models"])

    # 添加新模型
    st.subheader("添加新模型")

    with st.form("add_model_form"):
        col1, col2 = st.columns(2)

        with col1:
            provider = st.selectbox(
                "选择提供商",
                ["openai", "anthropic", "qwen", "local"],
                key="provider"
            )

            model_id = st.text_input(
                "模型ID",
                placeholder="例如: gpt-3.5-turbo",
                key="model_id"
            )

        with col2:
            model_name = st.text_input(
                "模型显示名称",
                placeholder="例如: GPT-3.5 Turbo",
                key="model_name"
            )

            max_tokens = st.number_input(
                "最大Token数",
                min_value=100,
                max_value=128000,
                value=4000,
                key="max_tokens"
            )

        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            step=0.1,
            value=0.7,
            key="temperature"
        )

        description = st.text_area(
            "模型描述",
            placeholder="描述这个模型的特点和适用场景",
            key="description"
        )

        submitted = st.form_submit_button("添加模型")

        if submitted:
            if not all([model_id, model_name, description]):
                st.error("请填写所有必填字段")
            else:
                # 添加新模型
                if provider not in config_loader.config["models"]:
                    config_loader.config["models"][provider] = {}

                config_loader.config["models"][provider][model_id] = {
                    "name": model_name,
                    "provider": provider,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "description": description
                }

                # 保存配置
                config_loader.save_config(config_loader.config)
                st.success(f"成功添加模型: {model_name}")

    # 删除模型
    st.subheader("删除模型")

    # 选择要删除的模型
    all_models = []
    for provider, models in config_loader.config["models"].items():
        for model_id, model_info in models.items():
            all_models.append((provider, model_id, model_info["name"]))

    if all_models:
        selected_delete = st.selectbox(
            "选择要删除的模型",
            [f"{info[2]} ({info[0]}/{info[1]})" for info in all_models],
            key="delete_model"
        )

        if st.button("删除模型", type="secondary"):
            # 解析选择
            provider, model_id = selected_delete.split(" (")[1].replace(")", "").split("/")

            # 删除模型
            if provider in config_loader.config["models"]:
                if model_id in config_loader.config["models"][provider]:
                    del config_loader.config["models"][provider][model_id]

                    # 如果提供商没有模型了，删除提供商
                    if not config_loader.config["models"][provider]:
                        del config_loader.config["models"][provider]

                    # 保存配置
                    config_loader.save_config(config_loader.config)
                    st.success(f"成功删除模型: {selected_delete}")

    # 导入/导出配置
    st.subheader("配置管理")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="导出配置",
            data=json.dumps(config_loader.config, ensure_ascii=False, indent=2),
            file_name="model_config.json",
            mime="application/json"
        )

    with col2:
        uploaded_file = st.file_uploader(
            "导入配置",
            type=["json"],
            key="import_config"
        )

        if uploaded_file:
            try:
                new_config = json.load(uploaded_file)
                # 验证配置格式
                if "models" in new_config:
                    config_loader.config = new_config
                    config_loader.save_config(config_loader.config)
                    st.success("配置导入成功！")
                else:
                    st.error("无效的配置文件格式")
            except Exception as e:
                st.error(f"导入失败: {str(e)}")

if __name__ == "__main__":
    model_manager()