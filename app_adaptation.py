"""
仿写应用 - Streamlit 界面

基于拆书逻辑的小说仿写系统
"""

import streamlit as st
import json
from typing import Dict, Any, Optional
from pathlib import Path
from services.novel_adaptation_engine import NovelAdaptationEngine, create_adaptation_config
from services.adaptation_interface import AdaptationInterface

# 设置页面配置
st.set_page_config(
    page_title="小说仿写系统",
    page_icon="📚",
    layout="wide"
)

# 标题
st.title("📚 小说仿写系统")
st.markdown("---")

# 初始化会话状态
if 'adaptation_config' not in st.session_state:
    st.session_state.adaptation_config = None
if 'adaptation_results' not in st.session_state:
    st.session_state.adaptation_results = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1

# 侧边栏配置
with st.sidebar:
    st.header("📋 配置面板")

    # 步骤指示器
    steps = ["选择书籍", "配置改编", "设置参数", "执行仿写", "查看结果"]
    for i, step in enumerate(steps, 1):
        if i == st.session_state.current_step:
            st.markdown(f"**{i}. {step}**")
        else:
            st.markdown(f"{i}. {step}")

    # 重置按钮
    if st.button("重置"):
        st.session_state.adaptation_config = None
        st.session_state.adaptation_results = None
        st.session_state.current_step = 1
        st.rerun()

# 主内容区域
def show_step1():
    """步骤1：选择原始书籍"""
    st.header("📚 步骤1：选择原始书籍")
    st.markdown("请选择要仿写的原始书籍文件：")

    # 选项1：上传新文件
    st.subheader("上传新文件")
    uploaded_file = st.file_uploader(
        "选择要上传的书籍文件",
        type=['txt', 'pdf', 'docx'],
        help="支持 TXT、PDF、DOCX 格式"
    )

    # 选项2：选择现有文件
    st.subheader("选择现有文件")
    import os
    current_dir = os.getcwd()
    files = [f for f in os.listdir(current_dir) if f.endswith(('.txt', '.pdf', '.docx'))]

    if files:
        selected_file = st.selectbox("选择书籍文件", files)
    else:
        st.warning("当前目录下没有找到可用的书籍文件")

    # 下一步按钮
    if st.button("下一步"):
        if uploaded_file:
            # 保存上传的文件
            import os
            upload_dir = os.path.join(current_dir, "data", "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.session_state.selected_book = file_path
        elif 'selected_file' in locals():
            st.session_state.selected_book = selected_file
        else:
            st.error("请选择或上传书籍文件")
            return
        st.session_state.current_step = 2
        st.rerun()

def show_step2():
    """步骤2：配置改编要求"""
    st.header("🎨 步骤2：配置改编要求")
    st.markdown("请输入你的改编要求：")

    # 世界观配置
    st.subheader("🌍 世界观配置")
    world_view = {}

    world_type = st.text_input("世界观类型（如：赛博朋克、仙侠、都市等）：")
    if world_type:
        world_view['type'] = world_type

    power_system = st.text_input("力量体系（如：基因武学、修真、魔法等）：")
    if power_system:
        world_view['power_system'] = power_system

    core_setting = st.text_input("核心设定（如：SSS级武圣、魔法学院等）：")
    if core_setting:
        world_view['core_setting'] = core_setting

    world_rules = st.text_input("世界规则（如：弱肉强食、魔法至上等）：")
    if world_rules:
        world_view['rules'] = world_rules

    # 角色配置
    st.subheader("👤 角色配置")
    characters = {}

    st.markdown("主角配置：")
    main_char_name = st.text_input("主角名字：")
    if main_char_name:
        characters[main_char_name] = {
            'type': st.text_input(f"{main_char_name}的类型："),
            'personality': st.text_input(f"{main_char_name}的性格特点："),
            'abilities': st.text_input(f"{main_char_name}的特殊能力："),
            'goals': st.text_input(f"{main_char_name}的行动目标：")
        }

    st.markdown("配角配置（可选）：")
    char_name = st.text_input("配角名字（或留空）：")
    if char_name:
        characters[char_name] = {
            'type': st.text_input(f"{char_name}的类型："),
            'personality': st.text_input(f"{char_name}的性格特点："),
            'abilities': st.text_input(f"{char_name}的特殊能力："),
            'goals': st.text_input(f"{char_name}的行动目标：")
        }

    # 剧情配置
    st.subheader("📖 剧情配置")
    plot = {}

    background = st.text_area("故事背景：")
    if background:
        plot['background'] = background

    conflict = st.text_area("核心冲突：")
    if conflict:
        plot['conflict'] = conflict

    brain_storm = st.text_area("故事脑洞：")
    if brain_storm:
        plot['brain_storm'] = brain_storm

    # 文风配置
    st.subheader("✍️ 文风配置")
    style = {}

    style_type = st.text_input("文风类型（如：古龙式、网文风、文艺风等）：")
    if style_type:
        style['type'] = style_type

    language = st.text_area("语言特点：")
    if language:
        style['language'] = language

    rhythm = st.text_area("叙事节奏：")
    if rhythm:
        style['rhythm'] = rhythm

    # 保存配置
    if st.button("保存配置"):
        config = create_adaptation_config(
            world_view=world_view,
            characters=characters,
            plot=plot,
            style=style
        )
        st.session_state.adaptation_config = config
        st.session_state.current_step = 3
        st.rerun()

def show_step3():
    """步骤3：设置仿写参数"""
    st.header("⚙️ 步骤3：设置仿写参数")
    st.markdown("请设置仿写参数：")

    # 章节数量
    chapters_to_adapt = st.number_input("要仿写的章节数量", min_value=1, max_value=20, value=3)

    # 目标字数
    target_word_count = st.number_input("每章目标字数", min_value=500, max_value=10000, value=2000)

    if st.button("开始仿写"):
        st.session_state.chapters_to_adapt = chapters_to_adapt
        st.session_state.target_word_count = target_word_count
        st.session_state.current_step = 4
        st.rerun()

def show_step4():
    """步骤4：执行仿写"""
    st.header("⚡ 步骤4：执行仿写")
    st.markdown("正在仿写中，请稍候...")

    # 模拟仿写过程
    import time
    import random

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i in range(100):
        time.sleep(0.1)
        progress_bar.progress(i + 1)
        status_text.text(f"仿写进度：{i + 1}%")

    # 生成模拟结果
    st.session_state.adaptation_results = {
        'adaptation_config': st.session_state.adaptation_config,
        'chapters': [
            {
                'chapter_number': 1,
                'chapter_title': '第一章：雨夜的重生与刀鸣',
                'adapted_content': '在酸雨中醒来，萧衍感到一阵熟悉的眩晕。十年前，他作为SSS级武圣"天刃"被挚友背叛，神级基因被剥夺，含恨陨落。如今，他重生在一个F级基因、身患"基因崩溃症"的病弱少年身上。雨夜街头，他偶遇手持粒子刀、对抗机械卫兵的少年"零"...\n\n萧衍在地下诊所用最后的积蓄购买抑制剂，尽显落魄。雨夜街头，偶遇手持粒子刀、对抗机械卫兵的少年"零"。萧衍发出组队邀请遭拒，反被警告"别跟着我"。萧衍进入地下黑市"巢都"，听闻盘踞此地的"铁臂帮"吹嘘自己的老大。S级改造人、"血蝎"集团的双胞胎杀手登场，气焰嚣张，瞬间废掉铁臂帮老大，意图吞并地盘...\n\n"零"为了一块稀有能源进入黑市，恰好与"血蝎"的目标冲突。"血蝎"嘲笑"零"的原始战法，并展示其碾压性的基因能力。"零"陷入苦战，险象环生。萧衍通过系统发现双胞胎的共感链接破绽，大喊："打左边那个的腰！""零"凭直觉听从，一刀重创左侧杀手，导致另一人也瞬间僵直..."零"抓住机会，一记拔刀斩秒杀二人。铁臂帮残余势力见状，企图对精疲力尽的"零"下手。萧衍启动系统推演，扔出一枚手术刀，精准切断偷袭者的手部神经。全场震慑，萧衍默默转身离开。"零"追上他，递过一瓶高纯度营养剂："这个，请你的。"'
            }
        ]
    }

    st.session_state.current_step = 5
    st.rerun()

def show_step5():
    """步骤5：查看结果"""
    st.header("📋 步骤5：查看结果")
    st.markdown("仿写完成！以下是仿写结果：")

    # 显示改编配置
    st.subheader("🎨 改编配置")
    st.json(st.session_state.adaptation_results['adaptation_config'])

    # 显示仿写章节
    st.subheader("📖 仿写章节")
    for chapter in st.session_state.adaptation_results['chapters']:
        st.markdown(f"### 第{chapter['chapter_number']}章：{chapter['chapter_title']}")
        st.text_area(
            "仿写内容",
            chapter['adapted_content'],
            height=300
        )

    # 保存选项
    st.subheader("💾 保存结果")
    output_path = st.text_input("保存路径（如：adapted_novel.json）：")

    if st.button("保存到文件"):
        if output_path:
            # 模拟保存
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(st.session_state.adaptation_results, f, ensure_ascii=False, indent=2)
            st.success(f"✅ 结果已保存到 {output_path}")
        else:
            st.warning("请输入保存路径")

    # 重新开始
    if st.button("重新开始"):
        st.session_state.adaptation_config = None
        st.session_state.adaptation_results = None
        st.session_state.current_step = 1
        st.rerun()

# 根据当前步骤显示相应内容
if st.session_state.current_step == 1:
    show_step1()
elif st.session_state.current_step == 2:
    show_step2()
elif st.session_state.current_step == 3:
    show_step3()
elif st.session_state.current_step == 4:
    show_step4()
elif st.session_state.current_step == 5:
    show_step5()