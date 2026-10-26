"""通知投递服务（邮件/站内信）"""
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self):
        self.smtp_host: Optional[str] = None
        self.smtp_port: int = 587
        self.smtp_user: Optional[str] = None
        self.smtp_pass: Optional[str] = None

    def configure(self, host: str, port: int, user: str, password: str):
        self.smtp_host = host
        self.smtp_port = port
        self.smtp_user = user
        self.smtp_pass = password

    async def send_email(self, to: str, subject: str, body: str) -> bool:
        if not self.smtp_host:
            logger.warning("SMTP not configured, skipping email to %s: %s", to, subject)
            return False
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.smtp_user
            msg["To"] = to
            msg.attach(MIMEText(body, "plain", "utf-8"))
            msg.attach(MIMEText(body.replace("\n", "<br>"), "html", "utf-8"))

            import smtplib
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            logger.info("Email sent to %s: %s", to, subject)
            return True
        except Exception as e:
            logger.error("Failed to send email to %s: %s", to, e)
            return False

    async def send_budget_alert(self, to: str, user_id: int, category_name: str,
                                 limit_amount: float, total_spent: float) -> bool:
        subject = f"【CoinWise 预算预警】{category_name} 已超支"
        body = (
            f"您好，\n\n"
            f"您在 {category_name} 分类的预算已超支：\n"
            f"  预算上限：¥{limit_amount:.2f}\n"
            f"  当前支出：¥{total_spent:.2f}\n\n"
            f"请登录 CoinWise 查看详情。\n\n"
            f"—— CoinWise AI 智能记账"
        )
        return await self.send_email(to, subject, body)

    async def send_anomaly_alert(self, to: str, user_id: int, message: str) -> bool:
        subject = "【CoinWise 安全提醒】检测到异常交易"
        body = (
            f"您好，\n\n"
            f"系统检测到以下异常交易：\n{message}\n\n"
            f"请登录 CoinWise 确认是否为本人操作。\n\n"
            f"—— CoinWise AI 智能记账"
        )
        return await self.send_email(to, subject, body)


notification_service = NotificationService()
