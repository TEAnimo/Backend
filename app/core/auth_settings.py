# app/core/auth_settings.py
import os

COOKIE_NAME = "access_token"
COOKIE_MAX_AGE = 15 * 60  # 15 min
SAMESITE = os.getenv("COOKIE_SAMESITE", "lax")  # "lax" o "none"
SECURE_COOKIE = os.getenv("ENV", "development") == "production"  # True en prod
RENEW_THRESHOLD_SECONDS = int(os.getenv("RENEW_THRESHOLD_SECONDS", str(5 * 60)))
