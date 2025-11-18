"""
订单查询路由
直接查询 PostgreSQL 并调用 n8n 发送邮件
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.crud import get_order_by_id
from app.deps import get_db
from app.clients.n8n_client import send_order_email_sync
from app.utils.response import create_response
from app.utils.logger import logger

router = APIRouter()


class SendEmailRequest(BaseModel):
    order_id: str


@router.get("/query")
async def order_query(
    order_id: str = Query(..., description="订单ID"),
    db: Session = Depends(get_db)
):
    """
    订单查询接口
    
    1. 从 PostgreSQL 查询订单信息
    2. 返回订单信息（不自动发送邮件）
    
    Args:
        order_id: 订单ID
        db: 数据库会话
        
    Returns:
        dict: 订单信息
    """
    try:
        logger.info(f"查询订单: {order_id}")
        
        # 查询订单
        order = get_order_by_id(db, order_id)
        
        if not order:
            logger.warning(f"订单不存在: {order_id}")
            return create_response(
                data=None,
                message=f"未找到订单 {order_id}",
                success=False,
                status_code=404,
                error="订单不存在"
            )
        
        # 转换为字典
        order_dict = order.to_dict() if hasattr(order, 'to_dict') else {
            "id": order.id,
            "order_id": order.order_id,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "product": order.product,
            "status": order.status,
            "amount": order.amount,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None
        }
        
        return create_response(
            data={**order_dict, "can_send_email": True},
            message="订单查询成功，如需发送邮件请先确认",
            success=True
        )
        
    except Exception as e:
        logger.error(f"订单查询失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"订单查询失败: {str(e)}"
        )


@router.post("/send-email")
async def trigger_order_email(
    request: SendEmailRequest,
    db: Session = Depends(get_db)
):
    """
    发送订单邮件通知（需要用户确认后调用）
    """
    try:
        logger.info(f"收到发送订单邮件请求: {request.order_id}")
        order = get_order_by_id(db, request.order_id)
        
        if not order:
            logger.warning(f"订单不存在，无法发送邮件: {request.order_id}")
            return create_response(
                data=None,
                message=f"未找到订单 {request.order_id}",
                success=False,
                status_code=404,
                error="订单不存在"
            )
        
        # 发送邮件
        try:
            send_order_email_sync(order)
            logger.info(f"订单邮件发送成功: {request.order_id}")
            return create_response(
                data={"order_id": request.order_id},
                message="邮件已发送至客户邮箱",
                success=True
            )
        except Exception as e:
            logger.error(f"发送订单邮件失败: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"发送邮件失败: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理发送邮件请求失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"发送邮件失败: {str(e)}"
        )

