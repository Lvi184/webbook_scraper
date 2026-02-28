import json
from pathlib import Path

class ConfigLoader:
    """配置加载器"""

    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 如果配置文件不存在，使用默认配置
            return self._get_default_config()

    def _get_default_config(self):
        """获取默认配置"""
        return {
            "models": {
                "openai": {
                    "gpt-3.5-turbo": {
                        "name": "GPT-3.5 Turbo",
                        "provider": "openai",
                        "max_tokens": 4000,
                        "temperature": 0.7,
                        "description": "快速高效，适合一般任务"
                    }
                },
                "qwen": {
                    "qwen-turbo": {
                        "name": "Qwen Turbo",
                        "provider": "qwen",
                        "max_tokens": 4000,
                        "temperature": 0.7,
                        "description": "阿里云千问模型"
                    }
                },
                "anthropic": {
                    "claude-3-haiku": {
                        "name": "Claude 3 Haiku",
                        "provider": "anthropic",
                        "max_tokens": 4096,
                        "temperature": 0.7,
                        "description": "Anthropic Claude模型"
                    }
                },
                "local": {
                    "llama2": {
                        "name": "Llama 2",
                        "provider": "local",
                        "max_tokens": 2048,
                        "temperature": 0.7,
                        "description": "本地部署的Llama 2模型"
                    }
                }
            },
            "default_settings": {
                "model": "qwen-turbo",
                "provider": "qwen",
                "chunk_size": 1000,
                "unit_size": 5,
                "max_tokens": 2000,
                "temperature": 0.7
            }
        }

    def get_models(self):
        """获取所有模型"""
        return self.config["models"]

    def get_providers(self):
        """获取所有提供商"""
        return list(self.config["models"].keys())

    def get_models_by_provider(self, provider):
        """获取指定提供商的模型"""
        return self.config["models"].get(provider, {})

    def get_model_config(self, provider, model):
        """获取指定模型配置"""
        return self.config["models"].get(provider, {}).get(model)

    def get_default_settings(self):
        """获取默认设置"""
        return self.config["default_settings"]

    def save_config(self, config):
        """保存配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        self.config = config