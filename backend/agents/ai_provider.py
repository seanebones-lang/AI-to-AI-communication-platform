"""
Multi-Model AI Provider System
Supports Claude, GPT-4, Gemini, and local models
"""

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from enum import Enum
import os
import httpx
from datetime import datetime

class AIModelType(str, Enum):
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    GPT_4_TURBO = "gpt-4-turbo-preview"
    GPT_4_O = "gpt-4o"
    GEMINI_PRO = "gemini-pro"
    GEMINI_PRO_VISION = "gemini-pro-vision"
    LLAMA_3_70B = "llama-3-70b"
    MISTRAL_LARGE = "mistral-large-latest"

class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.client = None
        
    @abstractmethod
    async def generate_response(self, messages: List[Dict], system_prompt: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        pass

class AnthropicProvider(AIProvider):
    """Claude AI provider"""
    
    def __init__(self, api_key: str, model: str = AIModelType.CLAUDE_3_SONNET):
        super().__init__(api_key, model)
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def generate_response(self, messages: List[Dict], system_prompt: str) -> Dict[str, Any]:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt,
                messages=messages
            )
            
            return {
                "content": response.content[0].text,
                "model": self.model,
                "provider": "anthropic",
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "model": self.model,
                "provider": "anthropic",
                "timestamp": datetime.now().isoformat()
            }
    
    async def health_check(self) -> bool:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except:
            return False

class OpenAIProvider(AIProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: str, model: str = AIModelType.GPT_4_TURBO):
        super().__init__(api_key, model)
        import openai
        self.client = openai.AsyncOpenAI(api_key=api_key)
    
    async def generate_response(self, messages: List[Dict], system_prompt: str) -> Dict[str, Any]:
        try:
            # Add system prompt to messages
            full_messages = [{"role": "system", "content": system_prompt}] + messages
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                max_tokens=2000,
                temperature=0.7
            )
            
            return {
                "content": response.choices[0].message.content,
                "model": self.model,
                "provider": "openai",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "model": self.model,
                "provider": "openai",
                "timestamp": datetime.now().isoformat()
            }
    
    async def health_check(self) -> bool:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return True
        except:
            return False

class GoogleProvider(AIProvider):
    """Google Gemini provider"""
    
    def __init__(self, api_key: str, model: str = AIModelType.GEMINI_PRO):
        super().__init__(api_key, model)
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model)
    
    async def generate_response(self, messages: List[Dict], system_prompt: str) -> Dict[str, Any]:
        try:
            # Convert messages to Gemini format
            prompt = system_prompt + "\n\n"
            for msg in messages:
                prompt += f"{msg['role']}: {msg['content']}\n"
            
            response = await asyncio.to_thread(self.client.generate_content, prompt)
            
            return {
                "content": response.text,
                "model": self.model,
                "provider": "google",
                "usage": {
                    "input_tokens": len(prompt.split()),
                    "output_tokens": len(response.text.split()) if response.text else 0
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "model": self.model,
                "provider": "google",
                "timestamp": datetime.now().isoformat()
            }
    
    async def health_check(self) -> bool:
        try:
            response = await asyncio.to_thread(self.client.generate_content, "test")
            return True
        except:
            return False

class LocalProvider(AIProvider):
    """Local model provider (Ollama, etc.)"""
    
    def __init__(self, api_key: str, model: str = AIModelType.LLAMA_3_70B, base_url: str = "http://localhost:11434"):
        super().__init__(api_key, model)
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
    
    async def generate_response(self, messages: List[Dict], system_prompt: str) -> Dict[str, Any]:
        try:
            # Convert to Ollama format
            prompt = system_prompt + "\n\n"
            for msg in messages:
                prompt += f"{msg['role']}: {msg['content']}\n"
            
            response = await self.client.post("/api/generate", json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            })
            
            result = response.json()
            
            return {
                "content": result.get("response", ""),
                "model": self.model,
                "provider": "local",
                "usage": {
                    "prompt_tokens": len(prompt.split()),
                    "output_tokens": len(result.get("response", "").split())
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "model": self.model,
                "provider": "local",
                "timestamp": datetime.now().isoformat()
            }
    
    async def health_check(self) -> bool:
        try:
            response = await self.client.get("/api/tags")
            return response.status_code == 200
        except:
            return False

class MultiModelManager:
    """Manages multiple AI models and provides failover"""
    
    def __init__(self):
        self.providers: Dict[str, AIProvider] = {}
        self.model_configs = {
            "corp_ai_primary": {
                "provider": "anthropic",
                "model": AIModelType.CLAUDE_3_SONNET,
                "fallback": ["openai", "google"]
            },
            "corp_ai_secondary": {
                "provider": "openai", 
                "model": AIModelType.GPT_4_TURBO,
                "fallback": ["anthropic", "google"]
            },
            "erp_ai_primary": {
                "provider": "anthropic",
                "model": AIModelType.CLAUDE_3_OPUS,
                "fallback": ["openai", "local"]
            },
            "erp_ai_secondary": {
                "provider": "google",
                "model": AIModelType.GEMINI_PRO,
                "fallback": ["anthropic", "openai"]
            }
        }
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available providers based on API keys"""
        
        # Anthropic Claude
        if os.getenv("ANTHROPIC_API_KEY"):
            self.providers["anthropic"] = AnthropicProvider(
                os.getenv("ANTHROPIC_API_KEY"),
                AIModelType.CLAUDE_3_SONNET
            )
        
        # OpenAI GPT
        if os.getenv("OPENAI_API_KEY"):
            self.providers["openai"] = OpenAIProvider(
                os.getenv("OPENAI_API_KEY"),
                AIModelType.GPT_4_TURBO
            )
        
        # Google Gemini
        if os.getenv("GOOGLE_API_KEY"):
            self.providers["google"] = GoogleProvider(
                os.getenv("GOOGLE_API_KEY"),
                AIModelType.GEMINI_PRO
            )
        
        # Local models (Ollama)
        if os.getenv("LOCAL_AI_ENABLED", "false").lower() == "true":
            self.providers["local"] = LocalProvider(
                "local",
                AIModelType.LLAMA_3_70B,
                os.getenv("LOCAL_AI_URL", "http://localhost:11434")
            )
    
    async def get_response(self, agent_type: str, messages: List[Dict], system_prompt: str) -> Dict[str, Any]:
        """Get response with automatic failover"""
        
        config = self.model_configs.get(agent_type, self.model_configs["corp_ai_primary"])
        primary_provider = config["provider"]
        fallbacks = config["fallback"]
        
        # Try primary provider
        if primary_provider in self.providers:
            provider = self.providers[primary_provider]
            if await provider.health_check():
                result = await provider.generate_response(messages, system_prompt)
                if "error" not in result:
                    result["used_provider"] = primary_provider
                    result["fallback_used"] = False
                    return result
        
        # Try fallback providers
        for fallback in fallbacks:
            if fallback in self.providers:
                provider = self.providers[fallback]
                if await provider.health_check():
                    result = await provider.generate_response(messages, system_prompt)
                    if "error" not in result:
                        result["used_provider"] = fallback
                        result["fallback_used"] = True
                        return result
        
        # All providers failed
        return {
            "error": "All AI providers failed",
            "attempted_providers": [primary_provider] + fallbacks,
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all providers"""
        status = {}
        
        for name, provider in self.providers.items():
            try:
                is_healthy = await provider.health_check()
                status[name] = {
                    "healthy": is_healthy,
                    "model": provider.model,
                    "type": type(provider).__name__
                }
            except Exception as e:
                status[name] = {
                    "healthy": False,
                    "error": str(e),
                    "model": provider.model,
                    "type": type(provider).__name__
                }
        
        return status
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        models = []
        
        for name, provider in self.providers.items():
            models.append({
                "provider": name,
                "model": provider.model,
                "type": type(provider).__name__,
                "healthy": True  # We'll check health separately
            })
        
        return models

# Global instance
multi_model_manager = MultiModelManager()
