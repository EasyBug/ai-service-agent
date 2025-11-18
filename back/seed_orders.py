"""
订单数据种子脚本
向数据库添加示例订单数据
"""
from app.db.session import SessionLocal
from app.db.crud import create_order
from app.utils.logger import logger


def seed_orders():
    """添加示例订单数据"""
    db = SessionLocal()
    
    try:
        logger.info("开始添加订单数据...")
        
        # 示例订单数据
        orders_data = [
            {
                "order_id": "ORD-2024-001",
                "customer_name": "张三",
                "customer_email": "zhangsan@example.com",
                "product": "智能手表 Pro",
                "status": "已发货",
                "amount": "1299.00"
            },
            {
                "order_id": "ORD-2024-002",
                "customer_name": "李四",
                "customer_email": "lisi@example.com",
                "product": "无线耳机 Air",
                "status": "处理中",
                "amount": "599.00"
            },
            {
                "order_id": "ORD-2024-003",
                "customer_name": "王五",
                "customer_email": "wangwu@example.com",
                "product": "智能音箱 Mini",
                "status": "待付款",
                "amount": "299.00"
            },
            {
                "order_id": "ORD-2024-004",
                "customer_name": "赵六",
                "customer_email": "zhaoliu@example.com",
                "product": "智能手表 Pro",
                "status": "已完成",
                "amount": "1299.00"
            },
            {
                "order_id": "ORD-2024-005",
                "customer_name": "钱七",
                "customer_email": "qianqi@example.com",
                "product": "无线充电器",
                "status": "已发货",
                "amount": "199.00"
            },
            {
                "order_id": "ORD-2024-006",
                "customer_name": "孙八",
                "customer_email": "sunba@example.com",
                "product": "智能手环",
                "status": "处理中",
                "amount": "399.00"
            },
            {
                "order_id": "ORD-2024-007",
                "customer_name": "周九",
                "customer_email": "zhoujiu@example.com",
                "product": "无线耳机 Air",
                "status": "已发货",
                "amount": "599.00"
            },
            {
                "order_id": "ORD-2024-008",
                "customer_name": "吴十",
                "customer_email": "wushi@example.com",
                "product": "智能音箱 Mini",
                "status": "已完成",
                "amount": "299.00"
            }
        ]
        
        # 添加订单
        created_count = 0
        skipped_count = 0
        
        for order_data in orders_data:
            try:
                # 检查订单是否已存在
                from app.db.crud import get_order_by_id
                existing_order = get_order_by_id(db, order_data["order_id"])
                
                if existing_order:
                    logger.info(f"订单 {order_data['order_id']} 已存在，跳过")
                    skipped_count += 1
                    continue
                
                # 创建订单
                order = create_order(db=db, **order_data)
                logger.info(f"✅ 创建订单: {order.order_id} - {order.customer_name} - {order.product}")
                created_count += 1
                
            except Exception as e:
                logger.error(f"创建订单 {order_data['order_id']} 失败: {str(e)}")
        
        logger.info(f"订单数据添加完成！")
        logger.info(f"  - 成功创建: {created_count} 个订单")
        logger.info(f"  - 已存在（跳过）: {skipped_count} 个订单")
        logger.info(f"  - 总计: {len(orders_data)} 个订单")
        
    except Exception as e:
        logger.error(f"添加订单数据失败: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_orders()

