import logging
import sys
import os
from datetime import timedelta
from typing import List
from loguru import logger
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret

from .loggingp import InterceptHandler

API_PREFIX = "/api"

JWT_TOKEN_PREFIX = "Token"  # noqa: S105
VERSION = "0.0.0"
ALGORITHM = "HS256"
config = Config(".env", os.environ)
DEBUG: bool = config("DEBUG", cast=bool, default=True)
# ACCESS_TOKEN_EXPIRE_MINUTES : int = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=15)
JWT_EXPIRATION_DELTA = timedelta(
    minutes=config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=600)
)
JWT_REFRESH_EXPIRATION_DELTA = timedelta(
    minutes=config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=10080)
)
CLIENT_ID:str = config("CLIENT_ID",cast=str,default="")
DATABASE_URL: str = config("DB_CONNECTION", cast=str, default="")
DATABASE_NAME: str = config("DB_NAME", cast=str, default="")
MAIL_USERNAME: str = config("MAIL_USERNAME", cast=str, default="")
MAIL_PASSWORD:str = config("MAIL_PASSWORD", cast=str, default="")
MAIL_FROM:str = config("MAIL_FROM", cast=str, default="")
API_HOST :str = config("API_HOST", cast=str, default="")
MAX_CONNECTIONS_COUNT: int = config("MAX_CONNECTIONS_COUNT", cast=int, default=10)
MIN_CONNECTIONS_COUNT: int = config("MIN_CONNECTIONS_COUNT", cast=int, default=10)

AWS_ACCESS_KEY_ID: str = config("AWS_ACCESS_KEY_ID", cast=str, default='')
AWS_SECRET_ACCESS_KEY: str = config("AWS_SECRET_ACCESS_KEY", cast=str, default='')
AWS_S3_BUCKET_NAME: str = config("AWS_S3_BUCKET_NAME", cast=str, default='')
AWS_REGION_NAME: str = config("AWS_REGION_NAME", cast=str, default='')


AWS_NOTIFICATION_PLATFORM_ARN: str = config("AWS_NOTIFICATION_PLATFORM_ARN", cast=str, default='')
AWS_NOTIFICATION_TOPIC_ARN: str = config("AWS_NOTIFICATION_TOPIC_ARN", cast=str, default='')
SECRET_KEY: Secret = config(
    "SECRET_KEY", cast=Secret, default="This is a secret key for development"
)

PROJECT_NAME: str = config("PROJECT_NAME", default="Visit Egypt")
ALLOWED_HOSTS: List[str] = config(
    "ALLOWED_HOSTS",
    cast=CommaSeparatedStrings,
    default="",
)

RESOURCES_NAMES: List[str] = ["places", "users", "items", "posts","ar"]
FILE_UPLOAD_SIZE : str = config("FILE_UPLOAD_SIZE", cast = str, default="4MB")
PRESIGNED_URL_TIME_INTERVAL: str = config("PRESIGNED_URL_TIME_INTERVAL", cast = str, default="3600")


# ELK
APM_SERVER_URL: str = config("APM_SERVER_URL", cast = str, default="")
APM_SERVER_TOKEN: str = config("APM_SERVER_TOKEN", cast = str, default="")
APM_SERVICE_NAME: str = config("APM_SERVICE_NAME", cast = str, default="")
ELK_ENABLED: str = config("ELK_ENABLED", cast = str, default="false")

# logging configuration
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
LOGGERS = ("uvicorn.asgi", "uvicorn.access")

logging.getLogger().handlers = [InterceptHandler()]
for logger_name in LOGGERS:
    logging_logger = logging.getLogger(logger_name)
    logging_logger.handlers = [InterceptHandler(level=LOGGING_LEVEL)]

logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])
