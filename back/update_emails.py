"""
更新数据库中所有订单的邮箱地址
"""
from app.db.session import SessionLocal
from app.db.models import Order
from app.utils.logger import logger

# 新的邮箱地址
NEW_EMAIL = "zhangbowei1994@126.com"

def update_all_emails():
    """更新所有订单的邮箱地址"""
    db = SessionLocal()
    try:
        # 查询所有订单
        orders = db.query(Order).all()
        
        if not orders:
            print("数据库中没有订单记录")
            return
        
        print(f"找到 {len(orders)} 条订单记录")
        print("=" * 60)
        
        # 更新每条订单的邮箱
        updated_count = 0
        for order in orders:
            old_email = order.customer_email
            order.customer_email = NEW_EMAIL
            updated_count += 1
            print(f"订单 {order.order_id}: {old_email} -> {NEW_EMAIL}")
        
        # 提交更改
        db.commit()
        
        print("=" * 60)
        print(f"✅ 成功更新 {updated_count} 条订单的邮箱地址")
        logger.info(f"更新了 {updated_count} 条订单的邮箱地址为 {NEW_EMAIL}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 更新失败: {str(e)}")
        logger.error(f"更新邮箱地址失败: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("开始更新订单邮箱地址...")
    print(f"新邮箱: {NEW_EMAIL}")
    print()
    update_all_emails()

