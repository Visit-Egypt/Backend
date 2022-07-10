from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware


from visitegypt.config.environment import (
    ALLOWED_HOSTS,
    API_PREFIX,
    DEBUG,
    PROJECT_NAME,
    VERSION,
    APM_SERVER_URL,
    APM_SERVER_TOKEN,
    APM_SERVICE_NAME,
    ELK_ENABLED
)
from visitegypt.infra.database.events import connect_to_db, close_db_connection
from visitegypt.api.errors.http_error import http_error_handler
from visitegypt.api.errors.validation_error import (
    http422_error_handler,
    http500_error_handler,
)
from visitegypt.api.routers.root import router
from visitegypt.infra.errors import InfrastructureException

from elasticapm.contrib.starlette import make_apm_client, ElasticAPM


def get_application() -> FastAPI:

    application = FastAPI(title=PROJECT_NAME, debug=DEBUG, version=VERSION)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_HOSTS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    if ELK_ENABLED == "true":
        apm_config = {
            'SERVICE_NAME': APM_SERVICE_NAME,
            'SERVER_URL': APM_SERVER_URL,
            'SECRET_TOKEN': APM_SERVER_TOKEN,
            'ENVIRONMENT': 'production',
            'CAPTURE_BODY':'all',
            'CAPTURE_HEADERS': True,
        }
        apm = make_apm_client(apm_config)
        application.add_middleware(ElasticAPM, client=apm)
    application.add_event_handler("startup", connect_to_db)
    application.add_event_handler("shutdown", close_db_connection)

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(InfrastructureException, http500_error_handler)
    application.add_exception_handler(RequestValidationError, http422_error_handler)

    application.include_router(router, prefix=API_PREFIX)

    return application


app = get_application()
