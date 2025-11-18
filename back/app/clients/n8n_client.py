"""
n8n Webhook 客户端模块
用于调用 n8n 自动化工作流
"""
import httpx
from typing import Dict, Any, Optional
from app.config import settings
from app.utils.logger import logger
from app.db.models import Order


async def send_order_email(order: Order) -> bool:
    """
    通过 n8n webhook 发送订单邮件
    
    Args:
        order: 订单对象
        
    Returns:
        bool: 是否发送成功
    """
    try:
        # 构建请求数据
        payload = {
            "order_id": order.order_id,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "product": order.product,
            "status": order.status,
            "amount": order.amount,
            "created_at": order.created_at.isoformat() if order.created_at else None
        }
        
        # 发送 POST 请求到 n8n webhook
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                settings.N8N_WEBHOOK_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            logger.info(f"成功发送订单邮件通知: {order.order_id}")
            return True
            
    except httpx.HTTPError as e:
        logger.error(f"n8n webhook 请求失败: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"发送订单邮件失败: {str(e)}")
        return False


def send_order_email_sync(order: Order) -> bool:
    """
    同步方式发送订单邮件（用于非异步环境）
    
    Args:
        order: 订单对象
        
    Returns:
        bool: 是否发送成功
    """
    # 检查 n8n webhook URL 是否配置
    if not settings.N8N_WEBHOOK_URL or settings.N8N_WEBHOOK_URL == "https://your-n8n-instance/webhook/order_email":
        logger.warning("n8n webhook URL 未配置，跳过邮件通知。请在 .env 文件中设置 N8N_WEBHOOK_URL")
        return False
    
    try:
        # 构建请求数据
        payload = {
            "order_id": order.order_id,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "product": order.product,
            "status": order.status,
            "amount": order.amount,
            "created_at": order.created_at.isoformat() if order.created_at else None
        }
        
        # 使用同步客户端发送请求
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                settings.N8N_WEBHOOK_URL,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            logger.info(f"成功发送订单邮件通知: {order.order_id}")
            return True
            
    except httpx.HTTPError as e:
        logger.error(f"n8n webhook 请求失败: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"发送订单邮件失败: {str(e)}")
        return False

