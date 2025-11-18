"""
更新现有用户的角色字段
为已存在的用户添加角色信息
"""
from app.db.session import SessionLocal
from app.db.models import User
from app.utils.logger import logger

def update_user_roles():
    """更新现有用户的角色"""
    db = SessionLocal()
    
    try:
        # 角色映射
        role_mapping = {
            "admin@example.com": "admin",
            "test@example.com": "test",
            "user@example.com": "user"
        }
        
        logger.info("开始更新用户角色...")
        
        updated_count = 0
        
        for email, role in role_mapping.items():
            user = db.query(User).filter(User.email == email).first()
            if user:
                if not hasattr(user, 'role') or user.role != role:
                    # 如果用户表还没有 role 字段，需要先添加列
                    # 这里假设已经通过数据库迁移添加了列
                    user.role = role
                    logger.info(f"✓ 更新用户角色: {email} -> {role}")
                    updated_count += 1
                else:
                    logger.info(f"用户 {email} 角色已是 {role}，跳过")
        
        db.commit()
        
        logger.info("=" * 50)
        logger.info(f"用户角色更新完成！")
        logger.info(f"  更新: {updated_count} 个用户")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"更新用户角色失败: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    update_user_roles()

