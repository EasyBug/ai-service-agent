"""
数据库初始化脚本
创建所有数据表
"""
from app.db.base import Base
from app.db.session import engine
from app.db import models  # 导入模型以确保表被注册
from app.utils.logger import logger


def init_database():
    """初始化数据库，创建所有表"""
    try:
        logger.info("开始初始化数据库...")
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        logger.info("数据库初始化成功！")
        logger.info("已创建以下表：")
        for table_name in Base.metadata.tables.keys():
            logger.info(f"  - {table_name}")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        raise


if __name__ == "__main__":
    init_database()

