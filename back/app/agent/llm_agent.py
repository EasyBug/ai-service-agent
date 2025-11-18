"""
LLM Agent
负责生成最终的自然语言回答
"""
from typing import Dict, Any
from app.clients.llm_client import get_llm_client
from app.utils.logger import logger


class LLMAgent:
    """LLM Agent 类"""
    
    def __init__(self):
        """初始化 LLM Agent"""
        self._llm_client = None
    
    @property
    def llm_client(self):
        """延迟加载 LLM 客户端"""
        if self._llm_client is None:
            self._llm_client = get_llm_client()
        return self._llm_client
    
    def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成最终回答
        
        Args:
            state: 当前状态字典，包含：
                - 'input' 或 'user_input': 用户输入
                - 'order': 订单信息（如果有）
                - 'documents': RAG 检索结果（如果有）
                
        Returns:
            Dict[str, Any]: 更新后的状态，包含 'response' 键
        """
        try:
            # 获取用户输入
            user_input = state.get("user_input") or state.get("input", "")
            
            if not user_input:
                logger.warning("用户输入为空，无法生成回答")
                return {**state, "response": "抱歉，我没有收到您的输入。"}
            
            # 构建上下文
            context = {}
            
            # 添加订单信息
            if "order" in state and state["order"]:
                context["order"] = state["order"]
            
            # 添加 RAG 检索结果
            if "documents" in state and state["documents"]:
                context["documents"] = state["documents"]
            
            # 如果需要邮件确认，在上下文中添加提示信息
            if state.get("order_email_prompt"):
                context["order_email_prompt"] = True
                context["order_customer_email"] = state.get("order_customer_email")
            
            # 生成回答
            response = self.llm_client.generate_response(
                user_input=user_input,
                context=context if context else None,
                email_confirmation_required=state.get("order_email_prompt", False),
                email_address=state.get("order_customer_email")
            )
            
            logger.info(f"成功生成回答，长度: {len(response)} 字符")
            
            return {
                **state,
                "response": response,
                "final_response": response
            }
            
        except Exception as e:
            logger.error(f"LLM Agent 处理失败: {str(e)}")
            error_msg = "抱歉，生成回答时出现错误，请稍后再试。"
            return {**state, "response": error_msg, "error": str(e)}

