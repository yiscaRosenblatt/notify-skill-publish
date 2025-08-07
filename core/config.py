# core/config.py

"""
Central Project Configuration File

This module defines the `Settings` class, which uses `pydantic.BaseSettings` to load and validate
application configuration from environment variables or default values.

Configurations include:
- MongoDB connection URI.
- SendGrid credentials (API key, sender email, and dynamic template ID for weekly reports).
- Celery configuration: broker URL, result backend, timezone, accepted content types, and task imports.

Note: The configuration is case-sensitive (`case_sensitive = True`).
"""


from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    MONGO_URI: str = "XXX"
    SENDGRID_API_KEY: str = "XXX"
    DEFAULT_EMAIL_FROM: str = "do-not-reply@betayeda.com"
    SENDGRID_SKILL_PUBLISHED_TEMPLATE_ID: str = "d-45f4edb43dfc48089015971ba9868794"

    CELERY: dict = {
        "broker_url": "redis://localhost:6379/0", #כתובת ה־broker של Celery
        "result_backend": "redis://localhost:6379/0", #המקום בו Celery שומר את התוצאות
        "timezone": "Asia/Jerusalem", #מגדיר את אזור הזמן
        "accept_content": ["json"],
        "task_serializer": "json",
        "imports": ("tasks.notify_skill_publish",),
    }

    class Config:
        case_sensitive = True


settings = Settings()
