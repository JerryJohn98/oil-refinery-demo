from http import HTTPStatus
from typing import Optional

import requests
from fastapi import HTTPException, Request, Response
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security.api_key import APIKeyBase, APIKeyCookie
from pydantic import BaseModel
from scripts.config.app_configurations import Auth
from scripts.core.constants.defaults import auth_endpoint_name, auth_error_msg
from scripts.logging.logging import logger


class MetaInfoSchema(BaseModel):
    project_id: Optional[str] = ""
    user_id: Optional[str] = ""
    language: Optional[str] = ""


class MetaInfoCookie(APIKeyBase):
    """
    Project ID backend using a cookie.
    """

    scheme: APIKeyCookie
    cookie_name: str

    def __init__(self, cookie_name: str = "projectId"):
        super().__init__()
        self.model: APIKey = APIKey(**{"in": APIKeyIn.cookie}, name=cookie_name)
        self.cookie_name = cookie_name
        self.scheme_name = self.__class__.__name__
        self.scheme = APIKeyCookie(name=self.cookie_name, auto_error=False)

    async def __call__(self, request: Request, response: Response):
        cookies = request.cookies
        cookie_json = {
            "projectId": cookies.get("projectId", request.headers.get("projectId")),
            "userId": cookies.get(
                "user_id", cookies.get("userId", request.headers.get("userId"))
            ),
            "language": cookies.get("language", request.headers.get("language")),
        }
        return MetaInfoSchema(
            project_id=cookie_json["projectId"],
            user_id=cookie_json["userId"],
            language=cookie_json["language"],
        )

    @staticmethod
    def set_response_info(cookie_name, cookie_value, response: Response):
        response.set_cookie(cookie_name, cookie_value, samesite="strict", httponly=True)
        response.headers[cookie_name] = cookie_value

    def authorize_cookie(self, req: Request):
        """function to call api for token authorization using cookie or header"""
        try:

            headers = req.headers
            header = (
                {"cookie": headers.get("Cookie")}
                if "Cookie" in headers
                else {"login-token": headers.get("login-token")}
            )
            host_name = Auth.host_name
            url = f"{host_name}{auth_endpoint_name}"
            authorization_response = requests.get(url, headers=header, verify=True)
            logger.info(authorization_response.json())
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail=auth_error_msg + str(e)
            )
        if authorization_response.status_code == HTTPStatus.OK:
            return authorization_response.json()["user_id"]
        else:
            raise HTTPException(
                status_code=authorization_response.status_code,
                detail=authorization_response.json()["detail"],
            )

    # to fetch decoded payload from request
    async def authorize_token(self, request: Request) -> dict:
        user_id = self.authorize_cookie(request)  # Assuming this method is synchronous

        # Attempt to get the payload from request.state
        if hasattr(request.state, "payload") and isinstance(
            request.state.payload, dict
        ):
            request_data = request.state.payload.copy()
        else:
            try:
                # Parse JSON body asynchronously
                request_data = await request.json()
            except Exception as e:
                raise HTTPException(
                    status_code=400, detail="Invalid JSON payload"
                ) from e

        # Ensure the payload is a dictionary
        if not isinstance(request_data, dict):
            raise HTTPException(status_code=400, detail="Payload must be a JSON object")

        # Add or update 'user_id'
        request_data["user_id"] = user_id
        return request_data
