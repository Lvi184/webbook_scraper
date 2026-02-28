"""
文本分块器使用示例

演示不同分块策略的使用方法
"""

from enhanced_text_chunker import (
    EnhancedTextChunker,
    ChunkStrategy,
    chunk_text_file
)
import json


# ==================== 示例文本 ====================

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
"""


LONG_TEXT_SAMPLE = """
这是一段较长的文本，用于演示自适应和混合分块策略。

在遥远的古代，有一个神秘的王国。这个王国被群山环绕，终年云雾缭绕，外人很难进入。

王国的居民们过着与世隔绝的生活，他们传承着古老的技艺和文化。这些技艺包括精湛的锻造工艺、神奇的炼金术，以及失传已久的古老咒语。

传说中，王国的中心有一座高塔，塔顶住着一位智者。这位智者已经活了数百年，见证了王国的兴衰变迁。

有一天，一个外来者意外地闯入了这个王国。他是一个年轻的冒险家，名叫亚历克斯。他听说了一个关于永恒宝藏的传说，于是决定一探究竟。

亚历克斯在茂密的森林中穿行，跋山涉水，历经千辛万苦。终于，他来到了王国的边缘。

守卫着王国边界的是一位古老的战士。他手持一把锈迹斑斑的长剑，但眼神中依然透露出当年的威严。

"外来者，你为何来此？"老战士问道。

亚历克斯恭敬地回答："我听说这里有一个关于永恒宝藏的传说，特来寻访。"

老战士深深地看了他一眼，缓缓说道："永恒宝藏并非金银珠宝，而是更深邃的东西。"

亚历克斯困惑地问："那到底是什么呢？"

老战士微微一笑，说道："那是一个考验，一个只有真正勇者才能通过的考验。"

亚历克斯毫不犹豫地说道："我愿意接受这个考验。"

于是，老战士让开了道路。亚历克斯踏入了这片神秘的土地。

他穿过茂密的森林，越过湍急的河流，翻过高耸的山脉。每一段路程都充满了挑战，每一步都需要勇气和智慧。

终于，他来到了王国中心的高塔下。

高塔直插云霄，仿佛与天空相连。塔身刻满了古老的符文，散发着神秘的光芒。

亚历克斯深吸一口气，开始攀登高塔。台阶异常陡峭，每一步都需要全力以赴。

当他终于到达塔顶时，看到了那位传说中的智者。

智者盘坐在一张古老的蒲团上，双目微闭，仿佛正在冥想。

"年轻人，你终于来了。"智者缓缓睁开眼睛，眼中闪烁着智慧的光芒。

亚历克斯恭敬地行礼："晚辈亚历克斯，拜见智者。"

智者微微点头，说道："你所寻找的永恒宝藏，不在我这里，而在于你的内心。"

亚历克斯困惑不解："智者，我不明白您的意思。"

智者解释道："真正的永恒宝藏，是你在这段旅程中获得的勇气、智慧和成长。这些东西才是真正永恒的，不会随时间而消失。"

亚历克斯恍然大悟。他突然明白，这段旅程本身，就是最大的收获。

智者继续说道："当你离开这里，回到外面的世界时，你会发现，你已经不再是原来的你了。"

亚历克斯深深地鞠了一躬，说道："多谢智者指点。"

智者笑了，说："去吧，年轻人，去追寻你的真正宝藏吧。"

亚历克斯告别了智者，开始了他的归途。

当他回到王国边界时，老战士依然站在那里守候着。

"看来你已经找到了答案。"老战士说道。

亚历克斯点点头，说道："是的，我找到了。"

老战士欣慰地笑了："那就好，祝你在未来的道路上一切顺利。"

亚历克斯挥手告别，踏上了归程。

这段旅程，让他明白了人生中最珍贵的东西，不是外在的财富，而是内心的成长和智慧。
"""


def example_chapter_chunking():
    """示例1：按章节分块"""
    print("=" * 60)
    print("示例1：按章节分块")
    print("=" * 60)

    chunker = EnhancedTextChunker(strategy=ChunkStrategy.CHAPTER)
    chunks = chunker.chunk_text(NOVEL_SAMPLE)

    print(f"\n生成了 {len(chunks)} 个分块：\n")

    for i, chunk in enumerate(chunks, 1):
        print(f"分块 {i}:")
        print(f"  ID: {chunk.id}")
        print(f"  类型: {chunk.chunk_type}")
        print(f"  字数: {chunk.word_count}")
        if "chapter_title" in chunk.metadata:
            print(f"  章节标题: {chunk.metadata['chapter_title']}")
        print(f"  内容预览: {chunk.content[:80]}...")
        print()


def example_semantic_chunking():
    """示例2：语义分块"""
    print("=" * 60)
    print("示例2：语义分块（保持句子完整性）")
    print("=" * 60)

    chunker = EnhancedTextChunker(
        strategy=ChunkStrategy.SEMANTIC,
        chunk_size=200,
        overlap=50
    )
    chunks = chunker.chunk_text(LONG_TEXT_SAMPLE)

    print(f"\n生成了 {len(chunks)} 个分块：\n")

    for i, chunk in enumerate(chunks, 1):
        print(f"分块 {i}:")
        print(f"  ID: {chunk.id}")
        print(f"  字数: {chunk.word_count}")
        print(f"  内容预览: {chunk.content[:100]}...")
        if "keywords" in chunk.metadata:
            print(f"  关键词: {', '.join(chunk.metadata['keywords'][:3])}")
        print()


def example_hybrid_chunking():
    """示例3：混合策略分块"""
    print("=" * 60)
    print("示例3：混合策略（章节检测 + 语义分块）")
    print("=" * 60)

    chunker = EnhancedTextChunker(
        strategy=ChunkStrategy.HYBRID,
        chunk_size=300,
        enable_semantic=True
    )
    chunks = chunker.chunk_text(LONG_TEXT_SAMPLE)

    print(f"\n生成了 {len(chunks)} 个分块：\n")

    for i, chunk in enumerate(chunks, 1):
        print(f"分块 {i}:")
        print(f"  ID: {chunk.id}")
        print(f"  类型: {chunk.chunk_type}")
        print(f"  字数: {chunk.word_count}")
        if "chapter_title" in chunk.metadata:
            print(f"  章节标题: {chunk.metadata['chapter_title']}")
        if "topic" in chunk.metadata:
            print(f"  主题: {chunk.metadata['topic']}")
        print(f"  内容预览: {chunk.content[:100]}...")
        print()


def example_adaptive_chunking():
    """示例4：自适应分块"""
    print("=" * 60)
    print("示例4：自适应分块（根据内容密度调整）")
    print("=" * 60)

    # 创建一个段落密集度不同的文本
    varied_density_text = """
第一段。这是简短的段落。

第二段。这也是简短的。

第三部分

这是一个较长的段落，包含更多的内容和描述。它有更多的文字，密度较低。通过对比，我们可以看到不同段落的密度差异。
    """ * 10

    chunker = EnhancedTextChunker(
        strategy=ChunkStrategy.ADAPTIVE,
        chunk_size=500
    )
    chunks = chunker.chunk_text(varied_density_text)

    print(f"\n生成了 {len(chunks)} 个分块：\n")

    for i, chunk in enumerate(chunks, 1):
        print(f"分块 {i}:")
        print(f"  字数: {chunk.word_count}")
        print(f"  内容预览: {chunk.content[:100]}...")
        print()


def example_file_chunking():
    """示例5：对文件进行分块"""
    print("=" * 60)
    print("示例5：对文件进行分块")
    print("=" * 60)

    # 首先创建一个示例文件
    sample_file = "sample_novel.txt"
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(NOVEL_SAMPLE)

    # 使用便捷函数分块
    chunks = chunk_text_file(
        sample_file,
        strategy="hybrid",
        chunk_size=300
    )

    print(f"\n从文件生成了 {len(chunks)} 个分块：\n")

    for i, chunk in enumerate(chunks, 1):
        print(f"分块 {i}: {chunk['metadata'].get('chapter_title', 'N/A')}")
        print(f"  字数: {chunk['word_count']}")
        print(f"  内容: {chunk['content'][:60]}...")
        print()


def example_export_to_json():
    """示例6：导出为JSON"""
    print("=" * 60)
    print("示例6：导出为JSON格式")
    print("=" * 60)

    chunker = EnhancedTextChunker(strategy=ChunkStrategy.CHAPTER)
    chunks = chunker.chunk_text(NOVEL_SAMPLE)

    # 转换为字典列表
    chunks_dict = [chunk.to_dict() for chunk in chunks]

    # 导出到JSON
    output_file = "chunks_output.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunks_dict, f, ensure_ascii=False, indent=2)

    print(f"\n已将 {len(chunks)} 个分块导出到 {output_file}")
    print("\nJSON结构示例：")
    print(json.dumps(chunks_dict[0], ensure_ascii=False, indent=2))


def example_with_mineru():
    """示例7：使用MinerU解析（如果可用）"""
    print("=" * 60)
    print("示例7：使用MinerU解析文档")
    print("=" * 60)

    # 创建一个示例文件
    sample_file = "sample_document.txt"
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(NOVEL_SAMPLE + "\n" + LONG_TEXT_SAMPLE)

    chunker = EnhancedTextChunker(
        strategy=ChunkStrategy.HYBRID,
        use_mineru=True  # 尝试使用MinerU
    )

    # 尝试解析文档
    chunks = chunker.chunk_document(sample_file)

    if chunks:
        print(f"\n成功解析文档，生成了 {len(chunks)} 个分块")

        # 检查是否有MinerU元数据
        mineru_metadata_found = False
        for chunk in chunks:
            if any(key.startswith("mineru_") for key in chunk.metadata):
                mineru_metadata_found = True
                break

        if mineru_metadata_found:
            print("检测到MinerU解析的元数据")
        else:
            print("使用回退方法解析（MinerU可能不可用）")
    else:
        print("文档解析失败")


def main():
    """运行所有示例"""
    examples = [
        example_chapter_chunking,
        example_semantic_chunking,
        example_hybrid_chunking,
        example_adaptive_chunking,
        example_file_chunking,
        example_export_to_json,
        example_with_mineru,
    ]

    for example in examples:
        try:
            example()
            print("\n")
        except Exception as e:
            print(f"示例执行出错: {e}\n")

    # 清理临时文件
    import os
    for temp_file in ["sample_novel.txt", "sample_document.txt", "chunks_output.json"]:
        if os.path.exists(temp_file):
            os.remove(temp_file)


if __name__ == "__main__":
    main()
