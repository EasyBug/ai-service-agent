"""
统一响应格式模块
"""
from typing import Any, Optional, Dict
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class APIResponse(BaseModel):
    """统一 API 响应模型"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None
    error: Optional[str] = None


def create_response(
    data: Any = None,
    message: str = "操作成功",
    success: bool = True,
    status_code: int = 200,
    error: Optional[str] = None
) -> JSONResponse:
    """
    创建统一格式的 API 响应
    
    Args:
        data: 响应数据
        message: 响应消息
        success: 是否成功
        status_code: HTTP 状态码
        error: 错误信息
        
    Returns:
        JSONResponse: FastAPI JSON 响应
    """
    response_data = {
        "success": success,
        "message": message,
        "data": data
    }
    
    if error:
        response_data["error"] = error
        response_data["success"] = False
    
    return JSONResponse(
        content=response_data,
        status_code=status_code
    )

