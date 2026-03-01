"""
启动整合系统 - 拆书仿写一体化平台
"""

import streamlit as st

# 运行整合应用
st.set_page_config(
    page_title="拆书仿写一体化平台",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 导入并运行主应用
from app_unified import main_interface
main_interface()