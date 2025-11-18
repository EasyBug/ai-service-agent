"""
更新测试用户的密码为更强的密码
避免 Google 密码管理器警告
"""
from app.db.session import SessionLocal
from app.db.models import User
from app.utils.logger import logger

def update_user_passwords():
    """更新测试用户的密码"""
    db = SessionLocal()
    
    try:
        # 新密码映射（更强的密码）
        password_mapping = {
            "admin@example.com": "Admin@2024!Secure",
            "test@example.com": "Test@2024!Secure",
            "user@example.com": "User@2024!Secure"
        }
        
        logger.info("开始更新用户密码...")
        
        updated_count = 0
        
        for email, new_password in password_mapping.items():
            user = db.query(User).filter(User.email == email).first()
            if user:
                user.set_password(new_password)
                logger.info(f"✓ 更新用户密码: {email}")
                updated_count += 1
            else:
                logger.warning(f"用户不存在: {email}")
        
        db.commit()
        
        logger.info("=" * 50)
        logger.info(f"用户密码更新完成！")
        logger.info(f"  更新: {updated_count} 个用户")
        logger.info("=" * 50)
        logger.info("")
        logger.info("新密码：")
        for email, password in password_mapping.items():
            logger.info(f"  {email}: {password}")
        logger.info("")
        
    except Exception as e:
        logger.error(f"更新用户密码失败: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    update_user_passwords()

