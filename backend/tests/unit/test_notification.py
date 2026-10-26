"""单元测试：通知投递服务"""
import pytest
from unittest.mock import patch, MagicMock
from services.notification import NotificationService


@pytest.fixture
def service():
    svc = NotificationService()
    svc.configure("smtp.test.com", 587, "user@test.com", "pass")
    return svc


class TestNotificationService:
    @pytest.mark.asyncio
    async def test_send_budget_alert(self, service):
        result = await service.send_budget_alert(
            to="test@example.com",
            user_id=1,
            category_name="餐饮",
            limit_amount=1000,
            total_spent=1200,
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_unconfigured_service(self):
        svc = NotificationService()
        result = await svc.send_email("test@test.com", "Subject", "Body")
        assert result is False

    def test_configure_method(self):
        svc = NotificationService()
        assert svc.smtp_host is None
        svc.configure("smtp.gmail.com", 465, "user", "pass")
        assert svc.smtp_host == "smtp.gmail.com"
        assert svc.smtp_user == "user"

    @pytest.mark.asyncio
    async def test_send_anomaly_alert(self, service):
        result = await service.send_anomaly_alert(
            to="test@example.com",
            user_id=1,
            message="检测到异常大额交易",
        )
        assert result is False
