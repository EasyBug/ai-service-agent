"""
配置管理模块
从环境变量读取配置信息
"""
import os
from typing import Optional
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 尝试导入 pydantic_settings，如果不可用则使用 os.getenv
try:
    from pydantic_settings import BaseSettings  # type: ignore
    
    class Settings(BaseSettings):
        """应用配置类（使用 Pydantic Settings）"""
        
        # PostgreSQL 配置
        POSTGRES_HOST: str = "localhost"
        POSTGRES_PORT: int = 5432
        POSTGRES_DB: str = "ai_db"
        POSTGRES_USER: str = "admin"
        POSTGRES_PASSWORD: str = "admin123"
        
        # Redis 配置
        REDIS_HOST: str = "localhost"
        REDIS_PORT: int = 6379
        
        # Gemini API 配置
        GEMINI_API_KEY: str = ""
        
        # n8n Webhook 配置
        N8N_WEBHOOK_URL: str = "https://your-n8n-instance/webhook/order_email"
        
        # 应用配置
        DEBUG: bool = False
        LOG_LEVEL: str = "INFO"
        SECRET_KEY: str = "your-secret-key-change-in-production"
        
        class Config:
            env_file = ".env"
            case_sensitive = False
            # 允许从环境变量读取
            env_file_encoding = "utf-8"
            
except ImportError:
    # 如果 pydantic_settings 不可用，使用 os.getenv 方式
    class Settings:
        """应用配置类（使用 os.getenv）"""
        
        # PostgreSQL 配置
        POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
        POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
        POSTGRES_DB: str = os.getenv("POSTGRES_DB", "ai_db")
        POSTGRES_USER: str = os.getenv("POSTGRES_USER", "admin")
        POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "admin123")
        
        # Redis 配置
        REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
        REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
        
        # Gemini API 配置
        GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
        
        # n8n Webhook 配置
        N8N_WEBHOOK_URL: str = os.getenv(
            "N8N_WEBHOOK_URL",
            "https://your-n8n-instance/webhook/order_email"
        )
        
        # 应用配置
        DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
        LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
        SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")


# 创建全局配置实例
settings = Settings()

