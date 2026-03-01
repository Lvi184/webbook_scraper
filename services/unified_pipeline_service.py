"""
统一流水线服务 - 整合拆书和仿写功能
"""

import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from .book_analyzer import BookAnalyzer
from .novel_adaptation_engine import NovelAdaptationEngine
from .llm_client import LLMClient

logger = logging.getLogger(__name__)


class UnifiedPipelineService:
    """
    统一流水线服务

    功能：
    1. 协调拆书和仿写的完整流程
    2. 管理数据流转
    3. 提供统一的接口
    """

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.book_analyzer = BookAnalyzer(llm_client)
        self.adaptation_engine = NovelAdaptationEngine(llm_client)
        self.analysis_storage = Path("data/analysis")
        self.adaptation_storage = Path("data/adaptations")
        self.results_storage = Path("data/results")

        # 创建存储目录
        for path in [self.analysis_storage, self.adaptation_storage, self.results_storage]:
            path.mkdir(parents=True, exist_ok=True)

    def run_full_pipeline(
        self,
        file_data: Dict,
        adaptation_config: Dict,
        force_analysis: bool = False
    ) -> Dict:
        """
        运行完整流水线

        Args:
            file_data: 文件数据
            adaptation_config: 仿写配置
            force_analysis: 是否强制重新分析

        Returns:
            Dict: 整合后的完整结果
        """
        try:
            # 步骤1: 拆书分析
            # st.info("🔍 执行拆书分析...")  # 注释掉streamlit调用，因为这个service可能在非streamlit环境中使用
            analysis_result = self._run_analysis(file_data, force_analysis)

            # 步骤2: 保存分析结果
            analysis_path = self._save_analysis(analysis_result)

            # 步骤3: 加载分析结果到仿写引擎
            self.adaptation_engine.load_analysis_result(analysis_path)

            # 步骤4: 执行仿写
            # st.info("✍️ 执行仿写创作...")  # 注释掉streamlit调用
            adaptation_result = self.adaptation_engine.generate_adaptation(adaptation_config)

            # 步骤5: 保存仿写结果
            adaptation_path = self._save_adaptation(adaptation_result)

            # 步骤6: 整合结果
            full_result = self._create_unified_result(
                analysis_result,
                adaptation_result,
                analysis_path,
                adaptation_path
            )

            # 步骤7: 保存完整结果
            result_path = self._save_unified_result(full_result)

            return {
                'analysis_path': str(analysis_path),
                'adaptation_path': str(adaptation_path),
                'result_path': str(result_path),
                'data': full_result
            }

        except Exception as e:
            logger.error(f"流水线执行失败: {str(e)}")
            raise

    def _run_analysis(self, file_data: Dict, force_analysis: bool) -> Dict:
        """执行拆书分析"""
        # 检查是否已有分析结果
        filename = file_data['filename']
        analysis_file = self.analysis_storage / f"{filename}.json"

        if analysis_file.exists() and not force_analysis:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        # 执行新的分析
        return self.book_analyzer.analyze_book(file_data)

    def _save_analysis(self, analysis_result: Dict) -> Path:
        """保存分析结果"""
        filename = analysis_result['book_info']['filename']
        analysis_file = self.analysis_storage / f"{filename}.json"

        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)

        return analysis_file

    def _save_adaptation(self, adaptation_result: Dict) -> Path:
        """保存仿写结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"adaptation_{timestamp}.json"
        adaptation_file = self.adaptation_storage / filename

        with open(adaptation_file, 'w', encoding='utf-8') as f:
            json.dump(adaptation_result, f, ensure_ascii=False, indent=2)

        return adaptation_file

    def _save_unified_result(self, full_result: Dict) -> Path:
        """保存整合结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"unified_{timestamp}.json"
        result_file = self.results_storage / filename

        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(full_result, f, ensure_ascii=False, indent=2)

        return result_file

    def _create_unified_result(
        self,
        analysis_result: Dict,
        adaptation_result: Dict,
        analysis_path: Path,
        adaptation_path: Path
    ) -> Dict:
        """创建整合结果"""
        return {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'analysis_file': str(analysis_path),
                'adaptation_file': str(adaptation_path),
                'source_file': analysis_result['book_info']['filename']
            },
            'analysis': analysis_result,
            'adaptation': adaptation_result,
            'summary': {
                'original_chapters': analysis_result['book_info']['total_chapters'],
                'original_units': analysis_result['book_info']['total_units'],
                'adapted_chapters': len(adaptation_result.get('adapted_content', [])),
                'total_words': adaptation_result.get('total_words', 0)
            }
        }

    def load_existing_analysis(self, filename: str) -> Optional[Dict]:
        """加载已有的分析结果"""
        analysis_file = self.analysis_storage / f"{filename}.json"
        if analysis_file.exists():
            with open(analysis_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None