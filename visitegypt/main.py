from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware


from visitegypt.config.environment import ALLOWED_HOSTS, API_PREFIX, DEBUG, PROJECT_NAME, VERSION
from visitegypt.infra.database.events import connect_to_db, close_db_connection
from visitegypt.api.errors.http_error import http_error_handler
from visitegypt.api.errors.validation_error import http422_error_handler
from visitegypt.api.routers.root import router
def get_application() -> FastAPI:
    application = FastAPI(title=PROJECT_NAME, debug=DEBUG, version=VERSION)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_HOSTS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_event_handler("startup", connect_to_db)
    application.add_event_handler("shutdown", close_db_connection)

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, http422_error_handler)

    application.include_router(router, prefix=API_PREFIX)

    return application


app = get_application()
