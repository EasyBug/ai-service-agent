"""
订单 Agent
负责查询订单信息并触发 n8n 邮件通知
"""
import re
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.crud import get_order_by_id
from app.clients.n8n_client import send_order_email_sync
from app.utils.logger import logger


class OrderAgent:
    """订单 Agent 类"""
    
    def __init__(self, db: Optional[Session] = None):
        """
        初始化订单 Agent
        
        Args:
            db: 数据库会话，如果不提供则需要在 process 中处理
        """
        self.db = db
    
    def extract_order_id(self, text: str) -> Optional[str]:
        """
        从文本中提取订单ID
        使用多种方法：正则表达式 + LLM 备用方案
        
        Args:
            text: 输入文本
            
        Returns:
            Optional[str]: 提取到的订单ID，如果未找到返回 None
        """
        # 方法 1: 使用正则表达式匹配常见的订单ID格式
        patterns = [
            # 带连字符的格式：ORD-2024-001, ORDER-123456
            r'(?:订单|订单号|order)[：:\s]*([A-Z]{2,}[-_]?\d{4}[-_]?\d{3,})',
            r'([A-Z]{2,}[-_]?\d{4}[-_]?\d{3,})',  # ORD-2024-001, ORD_2024_001
            # 带冒号或空格的格式
            r'订单[：:]\s*([A-Z0-9\-_]+)',  # 订单：ORDER123, 订单: ORD-2024-001
            r'订单号[：:]\s*([A-Z0-9\-_]+)',  # 订单号：ORDER123
            r'order[：:]\s*([A-Z0-9\-_]+)',  # order: ORDER123
            # 纯字母+数字格式（不含连字符）
            r'([A-Z]{2,}\d{3,})',  # ORDER123, ORD123456
            # 纯数字格式（8位以上）
            r'(\d{8,})',  # 12345678
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                order_id = match.group(1).strip()
                # 验证订单ID格式（至少包含字母和数字）
                if len(order_id) >= 5:  # 最小长度检查
                    logger.info(f"通过正则表达式提取到订单ID: {order_id}")
                    return order_id
        
        # 方法 2: 如果正则表达式失败，使用 LLM 提取
        logger.info("正则表达式未匹配到订单ID，尝试使用 LLM 提取")
        try:
            from app.clients.llm_client import get_llm_client
            llm_client = get_llm_client()
            
            extract_prompt = f"""请从以下用户输入中提取订单ID。订单ID通常格式为：ORD-2024-001、ORDER123 等。

用户输入：{text}

请只返回订单ID，不要返回其他内容。如果找不到订单ID，返回"未找到"。

订单ID："""
            
            response = llm_client.generate_text(
                prompt=extract_prompt,
                temperature=0.1,
                max_tokens=50
            )
            
            # 清理响应
            order_id = response.strip()
            
            # 移除可能的引号、标点等
            order_id = re.sub(r'^["\']|["\']$', '', order_id)
            order_id = order_id.strip()
            
            # 验证提取结果
            if order_id and order_id.lower() not in ['未找到', 'not found', 'none', 'null', '']:
                # 再次用正则验证格式
                if re.search(r'[A-Z0-9\-_]{5,}', order_id, re.IGNORECASE):
                    logger.info(f"通过 LLM 提取到订单ID: {order_id}")
                    return order_id.upper()  # 统一转为大写
        
        except Exception as e:
            logger.warning(f"使用 LLM 提取订单ID失败: {str(e)}")
        
        return None
    
    def process(self, state: Dict[str, Any], db: Optional[Session] = None) -> Dict[str, Any]:
        """
        处理订单查询
        
        Args:
            state: 当前状态字典，包含 'user_input' 或 'input'
            db: 数据库会话（如果未在初始化时提供）
            
        Returns:
            Dict[str, Any]: 更新后的状态，包含 'order' 键
        """
        try:
            # 获取数据库会话
            session = db or self.db
            if not session:
                logger.error("数据库会话未提供")
                return {**state, "order": None, "error": "数据库连接失败"}
            
            # 获取用户输入
            user_input = state.get("user_input") or state.get("input", "")
            
            # 提取订单ID
            order_id = self.extract_order_id(user_input)
            
            if not order_id:
                logger.warning(f"未能从输入中提取订单ID: {user_input}")
                return {
                    **state,
                    "order": None,
                    "error": "未能识别订单ID，请提供订单号"
                }
            
            # 查询订单
            order = get_order_by_id(session, order_id)
            
            if not order:
                logger.warning(f"订单不存在: {order_id}")
                return {
                    **state,
                    "order": None,
                    "error": f"未找到订单 {order_id}"
                }
            
            logger.info(f"成功查询订单: {order_id}")
            
            return {
                **state,
                "order": order.to_dict() if hasattr(order, 'to_dict') else {
                    "order_id": order.order_id,
                    "customer_name": order.customer_name,
                    "product": order.product,
                    "status": order.status,
                    "amount": order.amount
                },
                "order_id": order_id,
                "order_email_prompt": True,
                "order_can_send_email": True,
                "order_customer_email": order.customer_email
            }
            
        except Exception as e:
            logger.error(f"订单 Agent 处理失败: {str(e)}")
            return {**state, "order": None, "error": str(e)}

