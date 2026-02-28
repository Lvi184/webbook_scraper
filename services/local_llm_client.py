"""
本地LLM客户端实现
支持使用本地部署的模型（如Ollama）
"""

import requests
import json
import time
from typing import Dict, List, Optional

class LocalLLMClient:
    """本地LLM客户端"""

    def __init__(self, api_base: str = "http://localhost:11434", model: str = "llama2"):
        self.api_base = api_base.rstrip('/')
        self.model = model
        self.max_retries = 3
        self.retry_delay = 2

    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """生成响应"""
        for attempt in range(self.max_retries):
            try:
                # 准请求数据
                data = {
                    "model": self.model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False
                }

                # 如果有系统提示，添加到请求中
                if system_prompt:
                    data["system"] = system_prompt

                # 发送请求
                response = requests.post(
                    f"{self.api_base}/api/generate",
                    json=data,
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "")
                else:
                    raise Exception(f"API请求失败: {response.status_code}")

            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"本地LLM调用失败: {str(e)}")
                time.sleep(self.retry_delay)
                self.retry_delay *= 2

    def list_models(self) -> List[Dict]:
        """列出可用的模型"""
        try:
            response = requests.get(f"{self.api_base}/api/tags")
            if response.status_code == 200:
                return response.json().get("models", [])
            else:
                return []
        except:
            return []

    def generate_structured_output(self, prompt: str, output_format: str = "json") -> Dict:
        """生成结构化输出"""
        # 添加格式要求
        format_prompt = f"""
        请严格按照{output_format}格式输出结果，不要添加任何其他解释。

        {prompt}
        """

        response = self.generate(format_prompt)

        if output_format == "json":
            try:
                return json.loads(response)
            except:
                return self._fix_json(response)
        else:
            return {"content": response}

    def _fix_json(self, json_str: str) -> Dict:
        """尝试修复JSON字符串"""
        # 移除可能的markdown标记
        json_str = json_str.replace('```json', '').replace('```', '')

        # 尝试提取JSON对象
        start = json_str.find('{')
        end = json_str.rfind('}')

        if start != -1 and end != -1:
            try:
                return json.loads(json_str[start:end+1])
            except:
                pass

        return {"error": "JSON解析失败", "raw": json_str}