"""
优化版文本分块和拆书分析使用示例

基于全维度结构化拆书方案的增强版分析器
"""

from optimized_book_analyzer import OptimizedBookAnalyzer
import json
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)

# 示例文本
NOVEL_SAMPLE = """
第一章 少年得志

江南水乡，烟雨朦胧。

李明轩站在小镇的码头边，望着远去的船只，心中充满了对未来的憧憬。他今年刚满十八岁，正是意气风发的年纪。

"明轩，该回家了。"母亲的声音从身后传来。

他转过身，看到母亲正站在屋檐下，手里提着一把油纸伞。"知道了，我这就回来。"

雨越下越大，母子二人快步向家中走去。

第二章 离别前夕

夜深了，雨还在下。

李明轩躺在床上，辗转反侧。明天他就要离开这个生活了十八年的小镇，去往京城求学。

窗外的雨声敲打着他的心房，让他难以入眠。

第三章 京城初识

京城的繁华超出了李明轩的想象。

街道上车水马龙，店铺林立。各种商贩的吆喝声此起彼伏，构成了一首繁华的都市交响曲。

"这就是京城吗？"他喃喃自语道，眼中闪烁着兴奋的光芒。

第四章 初遇挑战

在京城的第一天，李明轩就遇到了麻烦。

一个地痞流氓试图抢夺他的行囊，李明轩凭借家传的武艺，轻松将其制服。

第五章 新的开始

李明轩在京城找到了一份工作，开始了新的生活。

他结识了新的朋友，学习新的知识，逐渐适应了京城的生活。

第六章 意外发现

李明轩在工作中发现了一个秘密，这个秘密可能会改变他的命运。

第七章 决定行动

李明轩决定调查这个秘密，他开始收集证据，寻找真相。

第八章 面对危险

李明轩的调查引起了某些人的注意，他开始面临危险。

第九章 智慧取胜

李明轩凭借自己的智慧，成功化解了危险，保护了自己。

第十章 新的旅程

李明轩的冒险才刚刚开始，他将继续前行，追求自己的梦想。
"""

def example_optimized_analysis():
    """优化版分析器使用示例"""
    print("=" * 80)
    print("优化版书籍分析器使用示例")
    print("=" * 80)

    # 创建优化版分析器
    analyzer = OptimizedBookAnalyzer(
        llm_client=None,  # 这里需要实际的LLM客户端
        chunking_strategy="hybrid",
        chunk_size=1000
    )

    # 模拟分析（实际使用时需要真实的LLM客户端）
    print("\n1. 阶段1：前置预处理 - 全书剧情单元划分")
    print("   - 将全书划分为剧情单元（每5章为1个单元）")
    print("   - 计算每个单元的核心主题")

    print("\n2. 阶段2：顶层宏观拆书 - 全书核心总纲拆解")
    print("   - 世界观核心总纲")
    print("   - 全本核心大纲")
    print("   - 全本核心角色总设定")

    print("\n3. 阶段3：中层中观拆书 - 分剧情单元5维拆解")
    print("   - 单元大纲设计")
    print("   - 单元世界观设计")
    print("   - 单元人物塑造设计")
    print("   - 单元情绪设计")
    print("   - 单元角色设计校验")

    print("\n4. 阶段4：底层微观拆书 - 单章细纲全维度拆解")
    print("   - 本章核心定位")
    print("   - 本章剧情细纲")
    print("   - 本章核心创作逻辑拆解")
    print("   - 改编适配校验")

    print("\n优化特点：")
    print("✓ 严格遵循「先全局总纲→再分单元拆解→最后单章细纲」的顺序")
    print("✓ 所有拆解内容按固定模块分类，可单独提取、替换、复用")
    print("✓ 100%原文贴合，不主观编造、不过度解读")
    print("✓ 拆解下沉到单章的每一个情节节点、情绪节点、人设节点")
    print("✓ 增加改编适配校验模块，明确可替换和不可替换内容")

def example_unit_analysis():
    """单元分析示例"""
    print("\n" + "=" * 80)
    print("单元分析示例")
    print("=" * 80)

    # 模拟单元数据
    unit_data = {
        "unit_number": 1,
        "chapter_range": "第1-5章",
        "theme": "少年得志与成长",
        "content": NOVEL_SAMPLE
    }

    print("单元信息：")
    print(f"  - 单元编号：{unit_data['unit_number']}")
    print(f"  - 章节范围：{unit_data['chapter_range']}")
    print(f"  - 核心主题：{unit_data['theme']}")
    print(f"  - 字数：{len(unit_data['content'])}")

    print("\n5维拆解结果：")
    print("  1. 单元大纲设计：按情节推进顺序，清晰描述核心事件、关键转折、人物行动")
    print("  2. 单元世界观设计：分点拆解本单元中，世界观、力量体系的展现")
    print("  3. 单元人物塑造设计：分点拆解核心人物关系、关系演进过程")
    print("  4. 单元情绪设计：分点拆解每个情绪节点，包含情绪类型、铺垫逻辑")
    print("  5. 单元角色设计校验：明确本单元中，每个核心角色的行为是否符合全书总人设")

def example_chapter_analysis():
    """章节分析示例"""
    print("\n" + "=" * 80)
    print("章节分析示例")
    print("=" * 80)

    chapter_data = {
        "chapter_number": 1,
        "chapter_title": "第一章 少年得志",
        "content": NOVEL_SAMPLE.split('\n\n')[0]
    }

    print("章节信息：")
    print(f"  - 章节编号：{chapter_data['chapter_number']}")
    print(f"  - 章节标题：{chapter_data['chapter_title']}")
    print(f"  - 字数：{len(chapter_data['content'])}")

    print("\n全维度拆解结果：")
    print("  1. 本章核心定位：在全书中的作用、核心目标、核心冲突、与前后章联动")
    print("  2. 本章剧情细纲：开篇铺垫→事件触发→情节推进→爽点爆发→结尾钩子")
    print("  3. 本章核心创作逻辑拆解：爽点设计、节奏设计、人设塑造、世界观展现")
    print("  4. 改编适配校验：核心不可替换的剧情骨架、可替换内容、人设适配要点")

def example_adaptation_guide():
    """改编适配指南示例"""
    print("\n" + "=" * 80)
    print("改编适配指南示例")
    print("=" * 80)

    print("1. 角色/金手指替换改编")
    print("   - 对标模板：《全本核心角色总设定拆解》+ 分单元人物塑造设计 + 单章人设塑造拆解")
    print("   - 操作方法：确定要替换的原作角色，对标其核心功能、剧情定位、成长线，设计新角色")

    print("\n2. 世界观/时代背景替换改编")
    print("   - 对标模板：《全书世界观核心总纲》+ 分单元世界观设计 + 单章世界观展现拆解")
    print("   - 操作方法：对标原作的世界观核心逻辑，设计新的世界观、时代背景、力量体系")

    print("\n3. 全文仿写二次创作")
    print("   - 对标模板：全本所有拆书成果，从总纲到单章细纲")
    print("   - 操作方法：先完成角色、世界观的替换设计，对标全本核心大纲生成改编大纲")

    print("\n4. 多本融合创作")
    print("   - 对标模板：拆书成果库")
    print("   - 操作方法：把多本书的拆书成果融合，生成全新的故事大纲和内容")

def main():
    """运行所有示例"""
    example_optimized_analysis()
    example_unit_analysis()
    example_chapter_analysis()
    example_adaptation_guide()

    print("\n" + "=" * 80)
    print("使用说明：")
    print("1. 安装依赖：pip install -r requirements.txt")
    print("2. 运行应用：python start.py")
    print("3. 上传网文文件进行拆书分析")
    print("4. 查看分析结果，可用于仿写改编")
    print("=" * 80)

if __name__ == "__main__":
    main()