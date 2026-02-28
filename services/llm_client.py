import openai
import anthropic
import time
from typing import Dict, Optional
import json
from .local_llm_client import LocalLLMClient

class LLMClient:
    """LLM客户端封装 - 支持多个提供商"""

    def __init__(self, api_key: str, provider: str = "openai", model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.provider = provider
        self.model = model
        self.max_retries = 3
        self.retry_delay = 2

        # 初始化客户端
        self._init_client()

    def _init_client(self):
        """初始化客户端"""
        if self.provider == "openai":
            self.client = openai.OpenAI(api_key=self.api_key)
        elif self.provider == "anthropic":
            self.client = anthropic.Anthropic(api_key=self.api_key)
        elif self.provider == "local":
            self.client = LocalLLMClient(model=self.model)
        elif self.provider == "qwen":
            # qwen使用http直接调用，不需要初始化客户端
            pass
        else:
            raise ValueError(f"不支持的提供商: {self.provider}")

    def get_available_providers(self):
        """获取可用的提供商列表"""
        return ["openai", "anthropic", "qwen", "local"]

    def get_models_for_provider(self, provider):
        """获取指定提供商支持的模型"""
        if provider == "local":
            # 如果是本地模型，尝试获取可用模型列表
            try:
                local_client = LocalLLMClient()
                models = local_client.list_models()
                return [m["name"] for m in models]
            except:
                return ["llama2", "qwen-7b"]  # 默认模型
        elif provider == "qwen":
            return ["qwen-turbo", "qwen-plus", "qwen-max"]
        else:
            models = {
                "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                "anthropic": ["claude-3-haiku", "claude-3-sonnet", "claude-3-opus"]
            }
            return models.get(provider, [])

    def generate(self, prompt: str, system_prompt: str = None, temperature: float = 0.7, max_tokens: int = None) -> str:
        """生成响应"""
        max_tokens = max_tokens or self._get_default_max_tokens()

        if self.provider == "openai":
            return self._generate_openai(prompt, system_prompt, temperature, max_tokens)
        elif self.provider == "anthropic":
            return self._generate_anthropic(prompt, system_prompt, temperature, max_tokens)
        elif self.provider == "qwen":
            return self._generate_qwen(prompt, system_prompt, temperature, max_tokens)
        elif self.provider == "local":
            return self._generate_local(prompt, system_prompt, temperature, max_tokens)
        else:
            raise ValueError(f"不支持的提供商: {self.provider}")

    def _generate_openai(self, prompt: str, system_prompt: str = None, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """OpenAI API调用"""
        # 检查是否是qwen模型
        if "qwen" in self.model.lower():
            return self._generate_qwen(prompt, system_prompt, temperature, max_tokens)

        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                return response.choices[0].message.content

            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"OpenAI API调用失败: {str(e)}")
                time.sleep(self.retry_delay)
                self.retry_delay *= 2

    def _generate_qwen(self, prompt: str, system_prompt: str = None, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Qwen千问API调用"""
        import httpx

        # 使用标准的OpenAI格式
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 使用正确的API端点
        api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

        # 使用标准格式
        data = {
            "model": self.model,
            "input": {
                "messages": messages
            },
            "parameters": {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": 0.9
            }
        }

        for attempt in range(self.max_retries):
            try:
                response = httpx.post(
                    api_url,
                    headers=headers,
                    json=data,
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    return result["output"]["text"]
                else:
                    # 尝试使用另一种格式
                    try:
                        alternative_data = {
                            "model": self.model,
                            "messages": messages,
                            "temperature": temperature,
                            "max_tokens": max_tokens
                        }
                        response = httpx.post(
                            api_url,
                            headers=headers,
                            json=alternative_data,
                            timeout=60
                        )
                        if response.status_code == 200:
                            result = response.json()
                            return result["output"]["text"]
                    except:
                        pass
                    raise Exception(f"Qwen API调用失败: {response.status_code} - {response.text}")

            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"Qwen API调用失败: {str(e)}")
                time.sleep(self.retry_delay)
                self.retry_delay *= 2

    def _generate_anthropic(self, prompt: str, system_prompt: str = None, temperature: float = 0.7, max_tokens: int = 2000) -> str:
        """Anthropic API调用"""
        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text

            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise Exception(f"Anthropic API调用失败: {str(e)}")
                time.sleep(self.retry_delay)
                self.retry_delay *= 2

    def _generate_local(self, prompt: str, system_prompt: str = None, temperature: float = 0.7, max_tokens: int = 2048) -> str:
        """本地模型调用"""
        return self.client.generate(prompt, system_prompt, temperature, max_tokens)

    def generate_structured_output(self, prompt: str, output_format: str = "json") -> Dict:
        """生成结构化输出"""
        # 指定输出格式
        format_prompt = f"""
        请按照{output_format}格式输出结果。不要添加其他解释。

        {prompt}
        """

        response = self.generate(format_prompt)

        if output_format == "json":
            try:
                return json.loads(response)
            except:
                # 尝试修复JSON
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

    def batch_generate(self, prompts: list, max_concurrent: int = 3) -> list:
        """批量生成"""
        results = []

        # 分批处理
        for i in range(0, len(prompts), max_concurrent):
            batch = prompts[i:i+max_concurrent]
            batch_results = []

            for prompt in batch:
                result = self.generate(prompt)
                batch_results.append(result)

            results.extend(batch_results)

        return results

    def _get_default_max_tokens(self):
        """获取默认最大token数"""
        default_tokens = {
            "gpt-3.5-turbo": 4000,
            "gpt-4": 8000,
            "gpt-4-turbo": 128000,
            "claude-3-haiku": 4096,
            "claude-3-sonnet": 4096,
            "claude-3-opus": 4096,
            "qwen-turbo": 4000,
            "llama2": 2048,
            "qwen-7b": 2048
        }
        return default_tokens.get(self.model, 2000)