"""
认证路由
处理用户登录、注册等认证相关接口
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.db.crud import authenticate_user, create_user, get_user_by_email
from app.deps import get_db
from app.utils.response import create_response
from app.utils.logger import logger
from app.config import settings

router = APIRouter()

# JWT 配置
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30天

# OAuth2 方案（用于后续的 Token 验证）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class LoginRequest(BaseModel):
    """登录请求模型"""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """登录响应模型"""
    token: str
    email: str
    name: Optional[str] = None


class RegisterRequest(BaseModel):
    """注册请求模型"""
    email: EmailStr
    password: str
    name: Optional[str] = None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    创建 JWT Token
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
        
    Returns:
        str: JWT Token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    验证 JWT Token
    
    Args:
        token: JWT Token
        
    Returns:
        Optional[dict]: 解码后的数据，如果无效返回 None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


@router.post("/login")
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录接口
    
    Args:
        request: 登录请求（邮箱和密码）
        db: 数据库会话
        
    Returns:
        dict: 包含 token 和用户信息
    """
    try:
        logger.info(f"用户登录尝试: {request.email}")
        
        # 验证用户
        user = authenticate_user(db, request.email, request.password)
        
        if not user:
            logger.warning(f"登录失败: {request.email} - 邮箱或密码错误")
            return create_response(
                data=None,
                message="邮箱或密码错误",
                success=False,
                status_code=401,
                error="认证失败"
            )
        
        # 生成 Token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id},
            expires_delta=access_token_expires
        )
        
        logger.info(f"用户登录成功: {user.email}")
        
        return create_response(
            data={
                "token": access_token,
                "email": user.email,
                "name": user.name,
                "role": user.role
            },
            message="登录成功",
            success=True
        )
        
    except Exception as e:
        logger.error(f"登录处理失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"登录处理失败: {str(e)}"
        )


@router.post("/register")
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    用户注册接口
    
    Args:
        request: 注册请求（邮箱、密码、姓名）
        db: 数据库会话
        
    Returns:
        dict: 注册结果
    """
    try:
        logger.info(f"用户注册尝试: {request.email}")
        
        # 检查用户是否已存在
        existing_user = get_user_by_email(db, request.email)
        if existing_user:
            logger.warning(f"注册失败: {request.email} - 用户已存在")
            return create_response(
                data=None,
                message="该邮箱已被注册",
                success=False,
                status_code=400,
                error="用户已存在"
            )
        
        # 验证密码长度
        if len(request.password) < 6:
            return create_response(
                data=None,
                message="密码长度至少为6位",
                success=False,
                status_code=400,
                error="密码不符合要求"
            )
        
        # 创建用户
        user = create_user(
            db=db,
            email=request.email,
            password=request.password,
            name=request.name
        )
        
        logger.info(f"用户注册成功: {user.email}")
        
        return create_response(
            data={
                "email": user.email,
                "name": user.name
            },
            message="注册成功",
            success=True
        )
        
    except Exception as e:
        logger.error(f"注册处理失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"注册处理失败: {str(e)}"
        )

