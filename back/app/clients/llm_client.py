"""
LLM 客户端模块
封装 Google Gemini API 调用
支持 Gemini 2.5 Flash 的流式、多模态、JSON 模式和工具调用
"""
import os
from typing import List, Optional, Dict, Any, Iterator, Union, AsyncIterator
from google import genai
from app.config import settings
from app.utils.logger import logger


class LLMClient:
    """LLM 客户端类 - 支持 Gemini 2.5 Flash 的完整功能"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 LLM 客户端
        
        Args:
            api_key: Gemini API 密钥，如果不提供则从配置读取
        """
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.client = None
        self.model_name = "gemini-2.5-flash"
        self.embedding_model = "models/gemini-embedding-001"
        
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"初始化 Gemini 客户端失败: {str(e)}")
    
    def _ensure_client(self):
        """确保客户端已初始化"""
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY 未配置，请在 .env 文件中设置")
        if not self.client:
            self.client = genai.Client(api_key=self.api_key)
    
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Union[str, Iterator[str]]:
        """
        生成文本（支持流式输出）
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            temperature: 温度参数
            max_tokens: 最大 token 数
            stream: 是否使用流式输出
            
        Returns:
            str 或 Iterator[str]: 生成的文本或流式迭代器
        """
        try:
            self._ensure_client()
            
            # 构建生成配置
            generation_config = {
                "temperature": temperature,
            }
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            # 构建内容
            # 注意：google-genai 1.50+ 不支持 "system" role
            # 需要将 system_prompt 合并到 user message 中，或使用 system_instruction 参数
            if system_prompt:
                # 方法 1: 将 system prompt 合并到用户消息中
                full_prompt = f"{system_prompt}\n\n{prompt}"
                contents = [{"role": "user", "parts": [{"text": full_prompt}]}]
            else:
                contents = [{"role": "user", "parts": [{"text": prompt}]}]
            
            # 调用 Gemini API（适配 google-genai 1.50+）
            if stream:
                # 流式生成
                response_stream = self.client.models.generate_content_stream(
                    model=self.model_name,
                    contents=contents,
                    config=generation_config
                )
                
                def _stream_generator():
                    for chunk in response_stream:
                        if hasattr(chunk, 'text') and chunk.text:
                            yield chunk.text
                        elif hasattr(chunk, 'candidates') and chunk.candidates:
                            for candidate in chunk.candidates:
                                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                                    for part in candidate.content.parts:
                                        if hasattr(part, 'text') and part.text:
                                            yield part.text
                
                return _stream_generator()
            else:
                # 非流式生成
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=generation_config
                )
                
                # 提取文本
                if hasattr(response, 'text'):
                    return response.text.strip()
                elif hasattr(response, 'candidates') and response.candidates:
                    text_parts = []
                    for candidate in response.candidates:
                        if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                            for part in candidate.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    text_parts.append(part.text)
                    return "".join(text_parts).strip()
                else:
                    return str(response).strip()
            
        except Exception as e:
            logger.error(f"生成文本失败: {str(e)}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        生成文本嵌入向量
        
        Args:
            text: 输入文本
            
        Returns:
            List[float]: 嵌入向量
        """
        try:
            self._ensure_client()
            
            # 调用 Gemini Embedding API（适配 google-genai 1.50+）
            response = self.client.models.embed_content(
                model=self.embedding_model,
                content={"parts": [{"text": text}]}
            )
            
            # 提取嵌入向量
            if hasattr(response, 'embedding'):
                return response.embedding
            elif hasattr(response, 'values'):
                return list(response.values)
            else:
                raise ValueError("无法从响应中提取嵌入向量")
            
        except Exception as e:
            logger.error(f"生成嵌入向量失败: {str(e)}")
            # 尝试备用方法
            try:
                response = self.client.models.embed_content(
                    model=self.embedding_model,
                    content=text
                )
                if hasattr(response, 'embedding'):
                    return response.embedding
                return list(response.values) if hasattr(response, 'values') else []
            except:
                raise
    
    def classify_intent(self, user_input: str) -> str:
        """
        分类用户意图
        
        Args:
            user_input: 用户输入
            
        Returns:
            str: 意图类型 ('order', 'rag', 'chat')
        """
        system_prompt = """你是一个意图分类助手。请根据用户输入判断意图类型，只返回以下三种之一：
- 'order': 如果用户询问订单、工单、物流、发货等相关信息
- 'rag': 如果用户询问产品知识、使用说明、常见问题等需要从知识库检索的信息
- 'chat': 如果是一般性对话、闲聊、问候等

只返回一个单词：order、rag 或 chat"""
        
        try:
            response = self.generate_text(
                prompt=user_input,
                system_prompt=system_prompt,
                temperature=0.3
            )
            
            # 清理响应，只保留意图关键词
            intent = response.lower().strip()
            if "order" in intent:
                return "order"
            elif "rag" in intent:
                return "rag"
            else:
                return "chat"
                
        except Exception as e:
            logger.error(f"意图分类失败: {str(e)}")
            # 默认返回 chat
            return "chat"
    
    def generate_response(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        email_confirmation_required: bool = False,
        email_address: Optional[str] = None
    ) -> str:
        """
        生成回答（带上下文）
        
        Args:
            user_input: 用户输入
            context: 上下文信息（订单信息、RAG 检索结果等）
            
        Returns:
            str: 生成的回答
        """
        system_prompt = """你是一个专业的智能客服助手。请根据用户的问题和提供的上下文信息，给出准确、友好、有帮助的回答。
如果上下文中有订单信息，请详细说明订单状态。
如果上下文中有知识库检索结果，请基于这些信息回答。
如果没有相关上下文，请基于你的知识回答。"""
        
        # 构建包含上下文的提示
        prompt = user_input
        if context:
            context_str = "\n\n上下文信息：\n"
            if "order" in context:
                order = context["order"]
                if isinstance(order, dict):
                    context_str += f"订单信息：{order}\n"
                else:
                    context_str += f"订单信息：{order.to_dict() if hasattr(order, 'to_dict') else str(order)}\n"
            
            if "documents" in context:
                docs = context["documents"]
                context_str += f"知识库检索结果：\n"
                for i, doc in enumerate(docs, 1):
                    if isinstance(doc, dict):
                        context_str += f"{i}. {doc.get('text', doc.get('content', str(doc)))}\n"
                    else:
                        context_str += f"{i}. {str(doc)}\n"
            
            prompt = context_str + "\n\n用户问题：" + user_input
        
        if email_confirmation_required:
            prompt += (
                "\n\n重要指令：用户刚刚查询了订单信息，请在回答中先介绍订单详情，"
                "然后询问用户是否需要将订单信息发送到客户邮箱"
            )
            if email_address:
                prompt += f"{email_address}"
            prompt += (
                "。在用户明确表示需要发送之前不要发送，也不要声称已经发送；"
                "如果用户拒绝或未确认，请说明不会发送。"
            )
        
        result = self.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7
        )
        
        # 如果返回的是迭代器（流式），收集所有内容
        if isinstance(result, Iterator):
            return "".join(result)
        return result
    
    def generate_with_multimodal(
        self,
        prompt: str,
        images: Optional[List[Union[str, bytes]]] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """
        多模态生成（支持文本 + 图片）
        
        Args:
            prompt: 文本提示
            images: 图片列表（文件路径或字节数据）
            system_prompt: 系统提示
            temperature: 温度参数
            
        Returns:
            str: 生成的文本
        """
        try:
            self._ensure_client()
            
            # 构建内容
            parts = [{"text": prompt}]
            
            # 添加图片
            if images:
                for img in images:
                    if isinstance(img, str):
                        # 文件路径
                        with open(img, 'rb') as f:
                            img_data = f.read()
                        parts.append({
                            "inline_data": {
                                "mime_type": "image/jpeg",  # 可根据实际类型调整
                                "data": img_data
                            }
                        })
                    elif isinstance(img, bytes):
                        # 字节数据
                        parts.append({
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": img
                            }
                        })
            
            # 构建内容（不支持 system role）
            if system_prompt:
                # 将 system prompt 合并到用户消息中
                full_prompt = f"{system_prompt}\n\n{prompt}"
                contents = [{"role": "user", "parts": [{"text": full_prompt}] + parts[1:]}]
            else:
                contents = [{"role": "user", "parts": parts}]
            
            # 生成内容
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config={"temperature": temperature}
            )
            
            if hasattr(response, 'text'):
                return response.text.strip()
            elif hasattr(response, 'candidates') and response.candidates:
                text_parts = []
                for candidate in response.candidates:
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        for part in candidate.content.parts:
                            if hasattr(part, 'text') and part.text:
                                text_parts.append(part.text)
                return "".join(text_parts).strip()
            return str(response).strip()
            
        except Exception as e:
            logger.error(f"多模态生成失败: {str(e)}")
            raise
    
    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        生成 JSON 格式响应
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            temperature: 温度参数
            
        Returns:
            Dict[str, Any]: JSON 格式的响应
        """
        try:
            import json
            
            # 在系统提示中添加 JSON 格式要求
            json_system_prompt = system_prompt or ""
            json_system_prompt += "\n\n请以 JSON 格式返回结果。"
            
            response_text = self.generate_text(
                prompt=prompt,
                system_prompt=json_system_prompt,
                temperature=temperature
            )
            
            # 尝试解析 JSON
            # 移除可能的 markdown 代码块标记
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {str(e)}, 响应: {response_text[:100]}")
            raise ValueError(f"无法解析 JSON 响应: {str(e)}")
        except Exception as e:
            logger.error(f"生成 JSON 失败: {str(e)}")
            raise


# 创建全局 LLM 客户端实例（延迟初始化，避免启动时就需要 API key）
llm_client = None

def get_llm_client() -> LLMClient:
    """获取 LLM 客户端实例（单例模式）"""
    global llm_client
    if llm_client is None:
        llm_client = LLMClient()
    return llm_client

