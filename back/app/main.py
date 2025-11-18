"""
FastAPI 应用主入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import query_router, order_router, rag_router, auth_router
from app.utils.logger import setup_logger, logger
from app.config import settings

# 设置日志
setup_logger()

# 创建 FastAPI 应用
app = FastAPI(
    title="Smart Support Agent Backend",
    description="智能客服系统后端 API",
    version="0.1.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(
    auth_router.router,
    prefix="/auth",
    tags=["Auth"]
)

app.include_router(
    query_router.router,
    prefix="/query",
    tags=["Query"]
)

app.include_router(
    order_router.router,
    prefix="/order",
    tags=["Order"]
)

app.include_router(
    rag_router.router,
    prefix="/rag",
    tags=["RAG"]
)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    健康检查接口
    
    Returns:
        dict: 健康状态
    """
    return {
        "status": "healthy",
        "service": "smart-support-agent-backend",
        "version": "0.1.0"
    }


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("=" * 50)
    logger.info("Smart Support Agent Backend 启动中...")
    logger.info(f"环境: {'开发' if settings.DEBUG else '生产'}")
    logger.info(f"PostgreSQL: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
    logger.info(f"Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    logger.info("=" * 50)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("Smart Support Agent Backend 正在关闭...")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

