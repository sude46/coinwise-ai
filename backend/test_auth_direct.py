"""直接测试注册登录业务逻辑，不涉及 HTTP"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from infrastructure.factory import get_db_session
from services.auth import AuthService


async def test_register_then_login():
    """在同一个 session 里注册，再开新 session 登录"""
    # 1. 注册（写操作）
    async with get_db_session(for_write=True) as write_session:
        auth = AuthService(write_session)
        # 先删旧用户
        try:
            old = await auth.user_repo.get_by_username("testuser")
            if old:
                await write_session.delete(old)
                await write_session.commit()
                print("[清理] 删除旧用户 testuser")
        except Exception as e:
            print(f"[清理警告] {e}")

        # 重新获取 session（delete 后 session 可能失效，直接用同一个继续）
        user = await auth.register("testuser", "test@test.com", "123456")
        print(f"[注册成功] id={user.id}, username={user.username}")
        print(f"[密码哈希] {user.hashed_password}")

    # 2. 登录（读操作，模拟 get_db 从库）
    async with get_db_session(for_write=False) as read_session:
        auth = AuthService(read_session)
        user = await auth.authenticate("testuser", "123456")
        if user:
            print(f"[登录成功] id={user.id}, username={user.username}")
        else:
            print("[登录失败] authenticate 返回 None")

    # 3. 再测一次错误密码
    async with get_db_session(for_write=False) as read_session:
        auth = AuthService(read_session)
        user = await auth.authenticate("testuser", "wrongpassword")
        print(f"[错误密码测试] 结果: {'通过(异常!)' if user else '拒绝(正确)'}")

    # 4. bcrypt 独立验证测试
    from passlib.context import CryptContext
    ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    h = ctx.hash("123456")
    ok = ctx.verify("123456", h)
    print(f"[bcrypt 自检] hash+verify: {'OK' if ok else 'FAIL'}")


if __name__ == "__main__":
    asyncio.run(test_register_then_login())
