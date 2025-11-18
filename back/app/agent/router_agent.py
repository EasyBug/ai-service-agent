"""
路由 Agent
负责判断用户意图并路由到相应的处理流程
"""
from typing import Dict, Any
from app.clients.llm_client import get_llm_client
from app.utils.logger import logger


class RouterAgent:
    """路由 Agent 类"""
    
    def __init__(self):
        """初始化路由 Agent"""
        self._llm_client = None
    
    @property
    def llm_client(self):
        """延迟加载 LLM 客户端"""
        if self._llm_client is None:
            self._llm_client = get_llm_client()
        return self._llm_client
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理状态，判断用户意图
        
        Args:
            state: 当前状态字典，包含 'input' 键（用户输入）
            
        Returns:
            Dict[str, Any]: 更新后的状态，包含 'intent' 键
        """
        try:
            user_input = state.get("input", "")
            
            if not user_input:
                logger.warning("用户输入为空，默认返回 chat 意图")
                return {**state, "intent": "chat"}
            
            # 调用 LLM 分类意图
            intent = self.llm_client.classify_intent(user_input)
            
            logger.info(f"用户意图分类结果: {intent}, 输入: {user_input[:50]}...")
            
            return {
                **state,
                "intent": intent,
                "user_input": user_input
            }
            
        except Exception as e:
            logger.error(f"路由 Agent 处理失败: {str(e)}")
            # 出错时默认返回 chat
            return {**state, "intent": "chat"}

