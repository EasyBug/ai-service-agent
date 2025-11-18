"""
测试 n8n 邮件发送功能
"""
import sys
from app.db.session import SessionLocal
from app.db.models import Order
from app.clients.n8n_client import send_order_email_sync
from app.utils.logger import logger

def test_n8n_email(order_id: str = None):
    """测试 n8n 邮件发送"""
    db = SessionLocal()
    try:
        # 获取订单
        if order_id:
            order = db.query(Order).filter(Order.order_id == order_id).first()
            if not order:
                print(f"❌ 未找到订单: {order_id}")
                return False
        else:
            # 使用第一个订单
            order = db.query(Order).first()
            if not order:
                print("❌ 数据库中没有订单记录")
                return False
        
        print("=" * 60)
        print("测试 n8n 邮件发送功能")
        print("=" * 60)
        print(f"订单ID: {order.order_id}")
        print(f"客户姓名: {order.customer_name}")
        print(f"客户邮箱: {order.customer_email}")
        print(f"产品: {order.product}")
        print(f"状态: {order.status}")
        print(f"金额: {order.amount}")
        print()
        
        # 发送邮件
        print("正在调用 n8n webhook...")
        result = send_order_email_sync(order)
        
        print()
        if result:
            print("✅ 邮件发送成功！")
            print(f"请检查邮箱 {order.customer_email} 是否收到邮件")
            return True
        else:
            print("❌ 邮件发送失败")
            print("请检查：")
            print("1. n8n webhook URL 是否正确配置")
            print("2. n8n 工作流是否已激活")
            print("3. 网络连接是否正常")
            print("4. 查看上面的错误日志")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        logger.error(f"测试 n8n 邮件发送失败: {str(e)}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    # 可以指定订单ID，或使用第一个订单
    order_id = sys.argv[1] if len(sys.argv) > 1 else None
    test_n8n_email(order_id)

