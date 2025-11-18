"""
主查询路由
接入 LangGraph AgentFlow
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.agent.graph import process_query
from app.deps import get_db
from app.utils.response import create_response
from app.utils.logger import logger

router = APIRouter()


class QueryRequest(BaseModel):
    """查询请求模型"""
    query: str
    thread_id: str = "default"


class QueryResponse(BaseModel):
    """查询响应模型"""
    response: str
    intent: str = "chat"
    order: dict = None
    documents: list = None
    error: str = None


@router.post("/")
async def query_endpoint(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """
    主查询接口
    
    接收用户查询，通过 LangGraph 工作流处理：
    1. RouterAgent 判断意图
    2. 根据意图路由到相应 Agent
    3. LLMAgent 生成最终回答
    
    Args:
        request: 查询请求
        db: 数据库会话
        
    Returns:
        QueryResponse: 查询结果
    """
    try:
        logger.info(f"收到查询请求: {request.query[:50]}...")
        
        # 处理查询
        result = process_query(
            query=request.query,
            db_session=db,
            thread_id=request.thread_id
        )
        
        return create_response(
            data=result,
            message="查询处理成功",
            success=True
        )
        
    except Exception as e:
        logger.error(f"查询处理失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"查询处理失败: {str(e)}"
        )

