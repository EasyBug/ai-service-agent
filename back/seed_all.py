"""
一键添加所有测试数据
包括订单数据和向量数据库数据
"""
from seed_orders import seed_orders
from seed_vector_db import seed_vector_database
from app.utils.logger import logger


def seed_all():
    """添加所有测试数据"""
    logger.info("=" * 50)
    logger.info("开始添加所有测试数据...")
    logger.info("=" * 50)
    
    # 1. 添加订单数据
    logger.info("\n📦 步骤 1: 添加订单数据")
    logger.info("-" * 50)
    try:
        seed_orders()
    except Exception as e:
        logger.error(f"添加订单数据失败: {str(e)}")
        return False
    
    # 2. 添加向量数据库数据
    logger.info("\n📚 步骤 2: 添加向量数据库数据")
    logger.info("-" * 50)
    try:
        success = seed_vector_database()
        if not success:
            logger.warning("向量数据库数据添加失败，但订单数据已添加")
    except Exception as e:
        logger.error(f"添加向量数据库数据失败: {str(e)}")
        logger.warning("订单数据已添加，但向量数据库数据添加失败")
    
    logger.info("\n" + "=" * 50)
    logger.info("✅ 数据添加完成！")
    logger.info("=" * 50)
    logger.info("\n现在你可以：")
    logger.info("  1. 启动服务: uvicorn app.main:app --reload")
    logger.info("  2. 测试订单查询: GET /order/query?order_id=ORD-2024-001")
    logger.info("  3. 测试 RAG 查询: POST /query (询问产品相关问题)")


if __name__ == "__main__":
    seed_all()

