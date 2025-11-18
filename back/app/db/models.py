"""
数据库模型定义
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from passlib.context import CryptContext
from app.db.base import Base

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    """
    用户模型
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False, comment="用户邮箱")
    password_hash = Column(String, nullable=False, comment="密码哈希")
    name = Column(String, nullable=True, comment="用户姓名")
    role = Column(String, nullable=False, default="user", comment="用户角色: admin, test, user")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def verify_password(self, password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(password, self.password_hash)
    
    def set_password(self, password: str):
        """设置密码（自动加密）"""
        self.password_hash = pwd_context.hash(password)
    
    def __repr__(self):
        return f"<User(email='{self.email}', name='{self.name}')>"
    
    def to_dict(self):
        """转换为字典（不包含密码）"""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def has_permission(self, permission: str) -> bool:
        """检查用户是否有特定权限"""
        if permission == "rag_access":
            # 只有 admin 和 test 角色可以访问知识库
            return self.role in ["admin", "test"]
        return False


class Order(Base):
    """
    订单/工单模型
    """
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(String, unique=True, index=True, nullable=False, comment="订单ID")
    customer_name = Column(String, nullable=True, comment="客户姓名")
    customer_email = Column(String, nullable=True, comment="客户邮箱")
    product = Column(String, nullable=True, comment="产品名称")
    status = Column(String, nullable=False, default="pending", comment="订单状态")
    amount = Column(String, nullable=True, comment="订单金额")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<Order(order_id='{self.order_id}', status='{self.status}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "order_id": self.order_id,
            "customer_name": self.customer_name,
            "customer_email": self.customer_email,
            "product": self.product,
            "status": self.status,
            "amount": self.amount,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

