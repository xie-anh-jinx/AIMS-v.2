"""
Notification Engine — Dispatches notifications via multiple channels.
Phase 2: Mock implementations (logs to DB). Phase 3: Real integrations.
"""
import logging
import subprocess
from datetime import datetime
from typing import Optional

logger = logging.getLogger("NotificationEngine")

class NotificationEngine:
    def __init__(self, db_session):
        self.db = db_session

    def send(self, channel: str, recipient: str, message: str, student_id: Optional[int] = None) -> bool:
        """
        Dispatches a notification to the specified channel.
        Currently mocked — logs to notification_logs table.
        Ready to be wired to real providers in Phase 3.
        """
        from packages.database.models import NotificationLog

        try:
            if channel == "WHATSAPP":
                self._send_whatsapp(recipient, message)
            elif channel == "EMAIL":
                self._send_email(recipient, message)
            elif channel == "TELEGRAM":
                self._send_telegram(recipient, message)

            log = NotificationLog(
                student_id=student_id,
                channel=channel,
                recipient=recipient,
                message=message,
                status="SENT",
                sent_at=datetime.utcnow()
            )
            self.db.add(log)
            self.db.commit()
            logger.info(f"[{channel}] ✓ Sent to {recipient}")
            return True

        except Exception as e:
            log = NotificationLog(
                student_id=student_id,
                channel=channel,
                recipient=recipient,
                message=message,
                status="FAILED",
                sent_at=datetime.utcnow()
            )
            self.db.add(log)
            self.db.commit()
            logger.error(f"[{channel}] ✗ Failed to send to {recipient}: {e}")
            return False

    def _send_whatsapp(self, phone: str, message: str):
        """Send WhatsApp message via OpenClaw CLI (Baileys/WhatsApp Web).
        
        Requires: openclaw gateway running + WhatsApp linked via QR scan.
        Setup: openclaw channels add --channel whatsapp && openclaw channels login --channel whatsapp
        """
        # Ensure E.164 format (e.g. 08123... → +628123...)
        if phone.startswith('08'):
            formatted_phone = '+62' + phone[1:]
        elif not phone.startswith('+'):
            formatted_phone = '+' + phone
        else:
            formatted_phone = phone

        try:
            # Check if openclaw is available
            import shutil
            if not shutil.which('openclaw'):
                logger.warning(
                    f"[WHATSAPP] openclaw CLI not found. "
                    f"Install with: npm install -g openclaw\n"
                    f"Mock output for {formatted_phone}:\n{message}"
                )
                return

            result = subprocess.run(
                [
                    "openclaw", "message", "send",
                    "--channel", "whatsapp",
                    "--target", formatted_phone,
                    "--message", message,
                ],
                capture_output=True,
                text=True,
                timeout=30,
                check=True
            )
            logger.info(f"[WHATSAPP ✓] Sent via OpenClaw → {formatted_phone}")
            if result.stdout:
                logger.debug(f"OpenClaw stdout: {result.stdout.strip()}")

        except subprocess.CalledProcessError as e:
            logger.error(f"[WHATSAPP ✗] OpenClaw error for {formatted_phone}: {e.stderr.strip()}")
            raise Exception(f"OpenClaw delivery failed: {e.stderr.strip()}")
        except subprocess.TimeoutExpired:
            logger.error(f"[WHATSAPP ✗] OpenClaw timed out for {formatted_phone}")
            raise Exception("OpenClaw send timed out (30s)")

    def _send_email(self, email: str, message: str):
        """Mock Email via SMTP."""
        # Phase 3: Replace with smtplib or resend/sendgrid client
        logger.info(f"[EMAIL MOCK] → {email}\n{message}\n")

    def _send_telegram(self, chat_id: str, message: str):
        """Send Telegram message directly via Bot API.
        
        Avoids OpenClaw CLI to prevent getUpdates conflicts with custom bot.
        """
        import os
        # Bot token injected from config or hardcoded for now
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "8947130178:AAG8Kn3p-BwvN0AQdOz3qIq_h0AAyX68tHk")
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        try:
            import httpx
            # Use synchronous httpx or requests
            with httpx.Client() as client:
                response = client.post(url, json={
                    "chat_id": str(chat_id),
                    "text": message,
                    "parse_mode": "Markdown"
                }, timeout=10.0)
                
            if response.status_code == 200:
                logger.info(f"[TELEGRAM ✓] Sent directly to → chat_id={chat_id}")
            else:
                logger.error(f"[TELEGRAM ✗] API error for chat_id={chat_id}: {response.text}")
                
        except Exception as e:
            logger.error(f"[TELEGRAM ✗] Failed to send to chat_id={chat_id}: {e}")
