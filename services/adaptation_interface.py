"""
仿写界面 - 用户交互界面

提供用户友好的界面，让用户可以：
1. 输入改编要求
2. 配置仿写参数
3. 控制仿写过程
4. 查看仿写结果
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from .novel_adaptation_engine import NovelAdaptationEngine, create_adaptation_config

logger = logging.getLogger(__name__)


class AdaptationInterface:
    """
    仿写界面 - 用户交互界面

    特性：
    - 用户友好的输入界面
    - 改编配置管理
    - 仿写过程控制
    - 结果展示和导出
    """

    def __init__(
        self,
        llm_client,
        chunking_strategy: str = "hybrid",
        chunk_size: int = 1000,
        use_mineru: bool = False
    ):
        self.engine = NovelAdaptationEngine(
            llm_client=llm_client,
            chunking_strategy=chunking_strategy,
            chunk_size=chunk_size,
            use_mineru=use_mineru
        )
        self.current_config = None
        self.adaptation_results = None

    def start_interface(self) -> None:
        """启动仿写界面"""
        print("=" * 60)
        print("小说仿写系统 - 基于拆书逻辑的自动化仿写")
        print("=" * 60)
        print()

        # 1. 选择原始书籍
        original_book = self._select_original_book()
        if not original_book:
            print("❌ 未选择原始书籍，退出系统")
            return

        # 2. 配置改编要求
        adaptation_config = self._configure_adaptation()
        if not adaptation_config:
            print("❌ 未配置改编要求，退出系统")
            return

        # 3. 设置仿写参数
        adaptation_params = self._set_adaptation_params()
        if not adaptation_params:
            print("❌ 未设置仿写参数，退出系统")
            return

        # 4. 执行仿写
        self._execute_adaptation(original_book, adaptation_config, adaptation_params)

        # 5. 展示结果
        self._display_results()

    def _select_original_book(self) -> Optional[str]:
        """选择原始书籍"""
        print("📚 步骤1: 选择原始书籍")
        print("请选择要仿写的原始书籍文件：")

        # 获取当前目录下的文件
        import os
        current_dir = os.getcwd()
        files = [f for f in os.listdir(current_dir) if f.endswith(('.txt', '.pdf', '.docx'))]

        if not files:
            print("❌ 当前目录下没有找到可用的书籍文件")
            return None

        # 显示文件列表
        for i, file in enumerate(files, 1):
            print(f"{i}. {file}")

        # 用户选择
        while True:
            try:
                choice = int(input("请输入文件编号（或0退出）："))
                if choice == 0:
                    return None
                if 1 <= choice <= len(files):
                    return files[choice - 1]
                print("❌ 无效的选择，请重新输入")
            except ValueError:
                print("❌ 请输入有效的数字")

    def _configure_adaptation(self) -> Optional[Dict]:
        """配置改编要求"""
        print("\n🎨 步骤2: 配置改编要求")
        print("请输入你的改编要求：")

        # 世界观配置
        world_view = self._input_world_view_config()
        if not world_view:
            return None

        # 角色配置
        characters = self._input_character_config()
        if not characters:
            return None

        # 剧情配置
        plot = self._input_plot_config()
        if not plot:
            return None

        # 文风配置
        style = self._input_style_config()
        if not style:
            return None

        return create_adaptation_config(
            world_view=world_view,
            characters=characters,
            plot=plot,
            style=style
        )

    def _input_world_view_config(self) -> Dict:
        """输入世界观配置"""
        print("\n🌍 世界观配置：")
        print("请描述新的世界观设定（按Enter跳过）：")

        world_view = {}

        # 世界观类型
        world_type = input("世界观类型（如：赛博朋克、仙侠、都市等）：").strip()
        if world_type:
            world_view['type'] = world_type

        # 力量体系
        power_system = input("力量体系（如：基因武学、修真、魔法等）：").strip()
        if power_system:
            world_view['power_system'] = power_system

        # 核心设定
        core_setting = input("核心设定（如：SSS级武圣、魔法学院等）：").strip()
        if core_setting:
            world_view['core_setting'] = core_setting

        # 世界规则
        world_rules = input("世界规则（如：弱肉强食、魔法至上等）：").strip()
        if world_rules:
            world_view['rules'] = world_rules

        return world_view if world_view else {}

    def _input_character_config(self) -> Dict:
        """输入角色配置"""
        print("\n👤 角色配置：")
        print("请描述主要角色的设定（按Enter跳过）：")

        characters = {}

        # 主角配置
        print("\n主角配置：")
        main_char_name = input("主角名字：").strip()
        if main_char_name:
            characters[main_char_name] = {
                'type': input("角色类型（如：重生武圣、病弱贵公子等）：").strip(),
                'personality': input("性格特点：").strip(),
                'abilities': input("特殊能力：").strip(),
                'goals': input("行动目标：").strip()
            }

        # 配角配置
        print("\n配角配置（按Enter跳过）：")
        while True:
            char_name = input("配角名字（或按Enter结束）：").strip()
            if not char_name:
                break

            characters[char_name] = {
                'type': input(f"{char_name}的类型：").strip(),
                'personality': input(f"{char_name}的性格特点：").strip(),
                'abilities': input(f"{char_name}的特殊能力：").strip(),
                'goals': input(f"{char_name}的行动目标：").strip()
            }

        return characters if characters else {}

    def _input_plot_config(self) -> Dict:
        """输入剧情配置"""
        print("\n📖 剧情配置：")
        print("请描述剧情设定（按Enter跳过）：")

        plot = {}

        # 故事背景
        background = input("故事背景：").strip()
        if background:
            plot['background'] = background

        # 核心冲突
        conflict = input("核心冲突：").strip()
        if conflict:
            plot['conflict'] = conflict

        # 故事脑洞
        brain_storm = input("故事脑洞：").strip()
        if brain_storm:
            plot['brain_storm'] = brain_storm

        return plot if plot else {}

    def _input_style_config(self) -> Dict:
        """输入文风配置"""
        print("\n✍️ 文风配置：")
        print("请描述期望的文风（按Enter跳过）：")

        style = {}

        # 文风类型
        style_type = input("文风类型（如：古龙式、网文风、文艺风等）：").strip()
        if style_type:
            style['type'] = style_type

        # 语言特点
        language = input("语言特点：").strip()
        if language:
            style['language'] = language

        # 叙事节奏
        rhythm = input("叙事节奏：").strip()
        if rhythm:
            style['rhythm'] = rhythm

        return style if style else {}

    def _set_adaptation_params(self) -> Optional[Dict]:
        """设置仿写参数"""
        print("\n⚙️ 步骤3: 设置仿写参数")

        try:
            # 章节数量
            chapters_to_adapt = int(input("要仿写的章节数量（默认3）：") or "3")

            # 目标字数
            target_word_count = input("每章目标字数（默认2000，按Enter跳过）：").strip()
            target_word_count = int(target_word_count) if target_word_count else 2000

            return {
                'chapters_to_adapt': chapters_to_adapt,
                'target_word_count': target_word_count
            }

        except ValueError:
            print("❌ 无效的输入，请输入有效的数字")
            return None

    def _execute_adaptation(
        self,
        original_book: str,
        adaptation_config: Dict,
        adaptation_params: Dict
    ) -> None:
        """执行仿写"""
        print("\n⚡ 步骤4: 执行仿写")
        print("正在仿写中，请稍候...")

        try:
            self.adaptation_results = self.engine.adapt_novel(
                original_book_path=original_book,
                adaptation_config=adaptation_config,
                chapters_to_adapt=adaptation_params['chapters_to_adapt'],
                target_word_count=adaptation_params['target_word_count']
            )
            print("✅ 仿写完成！")
        except Exception as e:
            print(f"❌ 仿写失败：{e}")
            self.adaptation_results = None

    def _display_results(self) -> None:
        """展示结果"""
        if not self.adaptation_results:
            print("❌ 没有可展示的结果")
            return

        print("\n📋 仿写结果：")
        print("=" * 60)

        # 显示改编配置
        print("\n🎨 改编配置：")
        print(json.dumps(self.adaptation_results['adaptation_config'], ensure_ascii=False, indent=2))

        # 显示仿写章节
        print("\n📖 仿写章节：")
        for i, chapter in enumerate(self.adaptation_results['chapters'], 1):
            print(f"\n第{i}章: {chapter['chapter_title']}")
            print("-" * 40)
            print(chapter['adapted_content'][:500] + "..." if len(chapter['adapted_content']) > 500 else chapter['adapted_content'])

        # 保存选项
        save_choice = input("\n是否保存仿写结果？(y/n)：").strip().lower()
        if save_choice == 'y':
            output_path = input("请输入保存路径（如：adapted_novel.json）：").strip()
            if output_path:
                self.engine._save_adapted_novel(self.adaptation_results, output_path)
                print(f"✅ 结果已保存到 {output_path}")
            else:
                print("❌ 未提供保存路径")

    def run_interactive_mode(self) -> None:
        """运行交互模式"""
        self.start_interface()


# 便捷函数
def run_adaptation_interface(llm_client):
    """运行仿写界面的便捷函数"""
    interface = AdaptationInterface(llm_client=llm_client)
    interface.run_interactive_mode()