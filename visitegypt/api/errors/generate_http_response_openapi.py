from visitegypt.api.errors.http_error import HTTPErrorModel
import string

def generate_response_for_openapi(resource_name: str):
    return {
    404: {
    "model": HTTPErrorModel,
    "description": f"The {resource_name.lower()} was not found",
    "content": {
        "application/json": {
        "example": {"errors": [f"{string.capwords(resource_name)} not exist"], "status_code": "404"}
        }
     }   
    },
    401: {
    "model": HTTPErrorModel,
    "description": f"The {resource_name.lower()} was not authenticated",
    "content": {
        "application/json": {
        "example": {"errors": ["Unauthorized"], "status_code": "401"}
        }
     }   
    },
    500: {
    "model": HTTPErrorModel,
    "description": "Internal Server Error",
    "content": {
        "application/json": {
        "example": {"errors": ["Internal Server Error"], "status_code": "500"}
        }
     }   
    },
}