import os
import re
import pdfplumber
import docx
from typing import List, Dict, Tuple
from pathlib import Path

class FileParser:
    """文件解析服务 - 支持PDF、DOCX、TXT格式"""

    def __init__(self):
        self.supported_formats = {'.pdf', '.docx', '.txt'}

    def parse_file(self, file_path: str) -> Dict:
        """解析文件并返回结构化数据"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        ext = file_path.suffix.lower()

        if ext not in self.supported_formats:
            raise ValueError(f"不支持的文件格式: {ext}")

        # 提取文件基本信息
        filename = file_path.name
        content = ""

        # 根据文件类型解析内容
        if ext == '.pdf':
            content = self._parse_pdf(file_path)
        elif ext == '.docx':
            content = self._parse_docx(file_path)
        elif ext == '.txt':
            content = self._parse_txt(file_path)

        # 检测章节
        chapters = self._detect_chapters(content)

        return {
            "filename": filename,
            "file_path": str(file_path),
            "file_size": file_path.stat().st_size,
            "content": content,
            "chapters": chapters,
            "total_chapters": len(chapters)
        }

    def _parse_pdf(self, file_path: Path) -> str:
        """解析PDF文件"""
        content = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                content += page_text + "\n"
        return content.strip()

    def _parse_docx(self, file_path: Path) -> str:
        """解析DOCX文件"""
        doc = docx.Document(file_path)
        content = ""
        for para in doc.paragraphs:
            content += para.text + "\n"
        return content.strip()

    def _parse_txt(self, file_path: Path) -> str:
        """解析TXT文件"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 清理乱码和水印
        import re
        
        # 移除乱码字符（非中文字符、数字、标点的奇怪字符）
        content = re.sub(r'[\x00-\x1f\x7f-\xff]+', '', content)
        
        # 移除常见的网站水印
        watermarks = [
            r'www\.txtsk\.com',
            r'txt\.uu366\.com',
            r'�����������������Ԥ��',
            r'24Сʱ��ɾ��',
            r'�����ϲ���빺������ͼ�飡'
        ]
        
        for watermark in watermarks:
            content = re.sub(watermark, '', content, flags=re.IGNORECASE)
        
        # 移除重复的空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        return content.strip()

    def _detect_chapters(self, content: str) -> List[Dict]:
        """智能检测章节"""
        chapters = []

        # 常见的章节正则模式
        chapter_patterns = [
            r'\n第[一二三四五六七八九十百千万\d]+[章节卷回][^\n]*',  # 确保匹配换行后的章节标题
            r'\n[一二三四五六七八九十百千万\d]+、[^、]*',     # 一、格式
            r'\n[一二三四五六七八九十百千万\d]+\.[^\.]*',      # 1. 格式
        ]

        # 合并所有模式
        pattern = '|'.join(chapter_patterns)
        matches = list(re.finditer(pattern, content))

        if not matches:
            # 如果没有检测到章节，按固定长度分割
            return self._split_by_length(content)

        # 提取章节内容
        start = 0
        for i, match in enumerate(matches):
            chapter_title = match.group()
            chapter_start = match.start()

            # 获取章节内容（直到下一个章节前）
            if i < len(matches) - 1:
                chapter_end = matches[i + 1].start()
                chapter_content = content[start:chapter_end].strip()
            else:
                chapter_content = content[start:].strip()

            if chapter_content:  # 确保内容不为空
                # 清理章节标题中的特殊字符
                clean_title = re.sub(r'\n+', '', chapter_title).strip()
                chapters.append({
                    "chapter_number": i + 1,
                    "title": clean_title,
                    "content": chapter_content,
                    "word_count": len(chapter_content)
                })

            start = match.end()

        return chapters

    def _split_by_length(self, content: str, chapter_length: int = 5000) -> List[Dict]:
        """按长度分割章节（备用方案）"""
        chapters = []
        words = content.split()
        current_words = []
        word_count = 0

        for i, word in enumerate(words):
            current_words.append(word)
            word_count += len(word) + 1  # +1 for space

            if word_count >= chapter_length:
                chapters.append({
                    "chapter_number": len(chapters) + 1,
                    "title": f"第{len(chapters) + 1}章",
                    "content": ' '.join(current_words),
                    "word_count": word_count
                })
                current_words = []
                word_count = 0

        # 添加最后一章
        if current_words:
            chapters.append({
                "chapter_number": len(chapters) + 1,
                "title": f"第{len(chapters) + 1}章",
                "content": ' '.join(current_words),
                "word_count": word_count
            })

        return chapters