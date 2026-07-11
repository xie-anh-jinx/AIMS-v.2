"""
AIMS Telegram Bot — API Client
Terhubung ke FastAPI backend untuk fetch data real.
"""
import httpx
import logging

logger = logging.getLogger("TelegramBotAPI")
BASE_URL = "http://localhost:8000"


async def login(username: str, password: str) -> dict | None:
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(f"{BASE_URL}/auth/login",
                                  data={"username": username, "password": password})
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            logger.error(f"Login error: {e}")
    return None


async def get_students(token: str) -> list:
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"{BASE_URL}/students/",
                                 headers={"Authorization": f"Bearer {token}"})
            return r.json() if r.status_code == 200 else []
        except Exception as e:
            logger.error(f"get_students error: {e}")
            return []


async def get_student_records(nim: str, token: str) -> list:
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"{BASE_URL}/students/{nim}/records",
                                 headers={"Authorization": f"Bearer {token}"})
            return r.json() if r.status_code == 200 else []
        except Exception as e:
            logger.error(f"get_student_records error: {e}")
            return []


async def get_admin_overview(token: str) -> dict:
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"{BASE_URL}/admin/overview",
                                 headers={"Authorization": f"Bearer {token}"})
            return r.json() if r.status_code == 200 else {}
        except Exception as e:
            logger.error(f"get_admin_overview error: {e}")
            return {}


async def get_agent_logs(token: str, limit: int = 10) -> list:
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"{BASE_URL}/agent/logs/activity?limit={limit}",
                                 headers={"Authorization": f"Bearer {token}"})
            return r.json() if r.status_code == 200 else []
        except Exception as e:
            logger.error(f"get_agent_logs error: {e}")
            return []


async def trigger_agent_evaluation(token: str) -> bool:
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(f"{BASE_URL}/agent/evaluate-all",
                                  headers={"Authorization": f"Bearer {token}"})
            return r.status_code == 200
        except Exception as e:
            logger.error(f"trigger_agent error: {e}")
            return False
