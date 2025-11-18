"""
数据库 CRUD 操作
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.db.models import Order, User


def get_order_by_id(db: Session, order_id: str) -> Optional[Order]:
    """
    根据订单ID查询订单
    
    Args:
        db: 数据库会话
        order_id: 订单ID
        
    Returns:
        Optional[Order]: 订单对象，如果不存在返回 None
    """
    return db.query(Order).filter(Order.order_id == order_id).first()


def get_all_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
    """
    获取所有订单（分页）
    
    Args:
        db: 数据库会话
        skip: 跳过记录数
        limit: 返回记录数
        
    Returns:
        List[Order]: 订单列表
    """
    return db.query(Order).offset(skip).limit(limit).all()


def create_order(
    db: Session,
    order_id: str,
    customer_name: Optional[str] = None,
    customer_email: Optional[str] = None,
    product: Optional[str] = None,
    status: str = "pending",
    amount: Optional[str] = None
) -> Order:
    """
    创建新订单
    
    Args:
        db: 数据库会话
        order_id: 订单ID
        customer_name: 客户姓名
        customer_email: 客户邮箱
        product: 产品名称
        status: 订单状态
        amount: 订单金额
        
    Returns:
        Order: 创建的订单对象
    """
    order = Order(
        order_id=order_id,
        customer_name=customer_name,
        customer_email=customer_email,
        product=product,
        status=status,
        amount=amount
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def update_order_status(db: Session, order_id: str, status: str) -> Optional[Order]:
    """
    更新订单状态
    
    Args:
        db: 数据库会话
        order_id: 订单ID
        status: 新状态
        
    Returns:
        Optional[Order]: 更新后的订单对象，如果不存在返回 None
    """
    order = get_order_by_id(db, order_id)
    if order:
        order.status = status
        db.commit()
        db.refresh(order)
    return order


# ========== 用户相关 CRUD 操作 ==========

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    根据邮箱查询用户
    
    Args:
        db: 数据库会话
        email: 用户邮箱
        
    Returns:
        Optional[User]: 用户对象，如果不存在返回 None
    """
    return db.query(User).filter(User.email == email).first()


def create_user(
    db: Session,
    email: str,
    password: str,
    name: Optional[str] = None,
    role: str = "user"
) -> User:
    """
    创建新用户
    
    Args:
        db: 数据库会话
        email: 用户邮箱
        password: 用户密码（明文，会自动加密）
        name: 用户姓名
        
    Returns:
        User: 创建的用户对象
    """
    user = User(
        email=email,
        name=name or email.split("@")[0],  # 默认使用邮箱前缀作为姓名
        role=role,
    )
    user.set_password(password)  # 自动加密密码
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    验证用户登录
    
    Args:
        db: 数据库会话
        email: 用户邮箱
        password: 用户密码（明文）
        
    Returns:
        Optional[User]: 如果验证成功返回用户对象，否则返回 None
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not user.is_active:
        return None
    if not user.verify_password(password):
        return None
    return user

