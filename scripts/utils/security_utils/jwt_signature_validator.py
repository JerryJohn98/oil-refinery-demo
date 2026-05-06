from typing import Optional

import jwt
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware


class EncodedPayloadSignatureMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        jwt_secret: str,
        jwt_algorithms: str,
        protect_hosts: Optional[list] = None,
    ):
        super().__init__(app)
        self.jwt_secret = jwt_secret
        self.jwt_algorithms = jwt_algorithms
        self.protect_hosts = protect_hosts or []

    async def dispatch(self, request: Request, call_next):
        # Skip validation for GET requests
        if request.method == "GET":
            return await call_next(request)

        # Check if the host is protected
        # if request.client.host in self.protect_hosts:
        body = await request.body()
        try:
            # Decode the JWT payload from the body
            token = body.decode("utf-8")
            payload = self.decode_jwt(token)

            # Add the decoded payload to the request state for further use
            request.state.payload = payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="JWT token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=400, detail="Invalid JWT token")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error decoding JWT: {str(e)}")

        # Continue with the request
        response = await call_next(request)
        return response

    def decode_jwt(self, token: str):
        """
        Decodes the JWT token and returns the payload.
        """
        try:
            # Decode the JWT using the secret key and algorithm
            payload = jwt.decode(
                token, self.jwt_secret, algorithms=[self.jwt_algorithms]
            )
            return payload
        except jwt.PyJWTError as e:
            raise jwt.PyJWTError(f"JWT decoding error: {str(e)}")
