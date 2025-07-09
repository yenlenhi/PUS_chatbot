"""
Ollama service for LLM interactions
"""
import requests
import json
from typing import Dict, Any, Optional, List
from src.utils.logger import log
from config.settings import OLLAMA_BASE_URL, OLLAMA_MODEL


class OllamaService:
    """Service for interacting with Ollama LLM"""
    
    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = OLLAMA_MODEL):
        """
        Initialize Ollama service
        
        Args:
            base_url: Ollama server base URL
            model: Model name to use
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.session = requests.Session()
        self.session.timeout = 60
    
    def check_health(self) -> Dict[str, Any]:
        """
        Check if Ollama service is healthy
        
        Returns:
            Health status dictionary
        """
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model['name'] for model in models]
                
                return {
                    'status': 'healthy',
                    'available_models': model_names,
                    'target_model_available': self.model in model_names
                }
            else:
                return {
                    'status': 'unhealthy',
                    'error': f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e)
            }
    
    def pull_model(self) -> bool:
        """
        Pull the specified model if not available
        
        Returns:
            True if successful, False otherwise
        """
        try:
            log.info(f"Pulling model: {self.model}")
            
            response = self.session.post(
                f"{self.base_url}/api/pull",
                json={'name': self.model},
                stream=True
            )
            
            if response.status_code == 200:
                # Stream the response to show progress
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            if 'status' in data:
                                log.info(f"Pull status: {data['status']}")
                        except json.JSONDecodeError:
                            continue
                
                log.info(f"Successfully pulled model: {self.model}")
                return True
            else:
                log.error(f"Failed to pull model: {response.text}")
                return False
                
        except Exception as e:
            log.error(f"Error pulling model: {e}")
            return False
    
    def generate_response(self, prompt: str, system_prompt: Optional[str] = None, 
                         temperature: float = 0.7, max_tokens: Optional[int] = None) -> Optional[str]:
        """
        Generate response from Ollama
        
        Args:
            prompt: User prompt
            system_prompt: System prompt for context
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response or None if failed
        """
        try:
            # Prepare the request payload
            payload = {
                'model': self.model,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'temperature': temperature,
                    'repeat_penalty': 1.2,
                    'top_p': 0.8,
                    'top_k': 30,
                    'num_predict': 500
                }
            }

            if max_tokens:
                payload['options']['num_predict'] = max_tokens

            if system_prompt:
                payload['system'] = system_prompt

            log.info(f"Sending request to Ollama with model: {self.model}")
            log.debug(f"Prompt length: {len(prompt)} chars")
            log.debug(f"System prompt length: {len(system_prompt) if system_prompt else 0} chars")

            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload
            )

            log.info(f"Ollama response status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '').strip()

                log.info(f"Generated text length: {len(generated_text)} chars")
                log.debug(f"Ollama response: {generated_text[:100]}...")

                if not generated_text:
                    log.warning("Ollama returned empty response")
                    return None

                return generated_text
            else:
                log.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            log.error(f"Error generating response: {e}")
            return None
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> Optional[str]:
        """
        Chat with Ollama using conversation format
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature
            
        Returns:
            Generated response or None if failed
        """
        try:
            payload = {
                'model': self.model,
                'messages': messages,
                'stream': False,
                'options': {
                    'temperature': temperature
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                message = result.get('message', {})
                content = message.get('content', '').strip()
                
                return content
            else:
                log.error(f"Ollama chat API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            log.error(f"Error in chat: {e}")
            return None
    
    def get_model_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the current model
        
        Returns:
            Model information dictionary or None if failed
        """
        try:
            response = self.session.post(
                f"{self.base_url}/api/show",
                json={'name': self.model}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                log.error(f"Failed to get model info: {response.text}")
                return None
                
        except Exception as e:
            log.error(f"Error getting model info: {e}")
            return None
