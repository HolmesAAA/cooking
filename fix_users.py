#!/usr/bin/env python3
"""
检查和修复数据库中的用户密码哈希
"""
import sys
import logging
from database import cosmos_db
from auth import get_password_hash

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def check_users():
    """检查所有用户的密码哈希"""
    logger.info("=" * 60)
    logger.info("检查数据库中的用户...")
    logger.info("=" * 60)

    try:
        # 初始化数据库
        cosmos_db.initialize()

        # 查询所有用户
        query = "SELECT * FROM users u"
        items = list(
            cosmos_db.users_container.query_items(
                query=query, enable_cross_partition_query=True
            )
        )

        logger.info(f"\n找到 {len(items)} 个用户\n")

        for user in items:
            email = user.get("email", "未知")
            hashed_password = user.get("hashed_password", "")

            logger.info(f"用户: {email}")
            logger.info(f"  用户ID: {user.get('id', '未知')}")
            logger.info(f"  用户名: {user.get('username', '未知')}")
            logger.info(f"  创建时间: {user.get('created_at', '未知')}")
            logger.info(f"  密码哈希长度: {len(hashed_password)} 字节")

            # 检查密码哈希格式
            if not hashed_password:
                logger.error(f"  ⚠️  警告: 密码哈希为空！")
            elif len(hashed_password) > 200:
                logger.error(f"  ⚠️  警告: 密码哈希过长 ({len(hashed_password)} 字节)！")
            elif not hashed_password.startswith("$2b$"):
                logger.warning(f"  ⚠️  警告: 密码哈希格式不正确（应以 $2b$ 开头）")
            else:
                logger.info(f"  ✓ 密码哈希格式正常")

            logger.info("")

        return True

    except Exception as e:
        logger.error(f"检查失败: {e}", exc_info=True)
        return False


def fix_user_password(email: str, new_password: str):
    """修复用户密码"""
    logger.info("=" * 60)
    logger.info(f"修复用户密码: {email}")
    logger.info("=" * 60)

    try:
        # 初始化数据库
        cosmos_db.initialize()

        # 查找用户
        user = cosmos_db.get_user_by_email(email)
        if not user:
            logger.error(f"用户不存在: {email}")
            return False

        # 生成新的密码哈希
        new_hash = get_password_hash(new_password)
        logger.info(f"新密码哈希长度: {len(new_hash)} 字节")
        logger.info(f"新密码哈希前缀: {new_hash[:10]}...")

        # 更新用户
        user["hashed_password"] = new_hash
        cosmos_db.users_container.replace_item(item=user["id"], body=user)

        logger.info(f"✓ 成功更新用户密码: {email}")
        return True

    except Exception as e:
        logger.error(f"修复失败: {e}", exc_info=True)
        return False


def main():
    """主函数"""
    logger.info("用户密码诊断工具\n")

    # 检查所有用户
    success = check_users()

    if not success:
        logger.error("\n❌ 检查失败")
        return 1

    logger.info("\n" + "=" * 60)
    logger.info("检查完成")
    logger.info("=" * 60)
    logger.info("\n如果发现问题用户，可以使用以下命令修复：")
    logger.info("python fix_users.py --fix <email> <new_password>")

    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--fix":
        if len(sys.argv) < 4:
            logger.error("用法: python fix_users.py --fix <email> <new_password>")
            sys.exit(1)
        email = sys.argv[2]
        password = sys.argv[3]
        success = fix_user_password(email, password)
        sys.exit(0 if success else 1)
    else:
        sys.exit(main())
