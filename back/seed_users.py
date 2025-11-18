"""
初始化测试用户数据
"""
from app.db.session import SessionLocal
from app.db.crud import create_user, get_user_by_email
from app.utils.logger import logger


def seed_users():
    """初始化测试用户"""
    db = SessionLocal()
    
    try:
        # 测试用户列表
        # 注意：使用更强的密码以避免 Google 密码管理器警告
        test_users = [
            {
                "email": "admin@example.com",
                "password": "Admin@2024!Secure",
                "name": "管理员",
                "role": "admin"
            },
            {
                "email": "test@example.com",
                "password": "Test@2024!Secure",
                "name": "测试用户",
                "role": "test"
            },
            {
                "email": "user@example.com",
                "password": "User@2024!Secure",
                "name": "普通用户",
                "role": "user"
            }
        ]
        
        logger.info("开始初始化测试用户...")
        
        created_count = 0
        skipped_count = 0
        
        for user_data in test_users:
            # 检查用户是否已存在
            existing_user = get_user_by_email(db, user_data["email"])
            
            if existing_user:
                logger.info(f"用户已存在，跳过: {user_data['email']}")
                skipped_count += 1
                continue
            
            # 创建用户
            user = create_user(
                db=db,
                email=user_data["email"],
                password=user_data["password"],
                name=user_data["name"],
                role=user_data.get("role", "user")
            )
            
            logger.info(f"✓ 创建用户成功: {user.email} ({user.name})")
            created_count += 1
        
        logger.info("=" * 50)
        logger.info(f"用户初始化完成！")
        logger.info(f"  创建: {created_count} 个用户")
        logger.info(f"  跳过: {skipped_count} 个已存在的用户")
        logger.info("=" * 50)
        logger.info("")
        logger.info("测试账号：")
        for user_data in test_users:
            logger.info(f"  邮箱: {user_data['email']}")
            logger.info(f"  密码: {user_data['password']}")
            logger.info("")
        
    except Exception as e:
        logger.error(f"初始化用户失败: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()

