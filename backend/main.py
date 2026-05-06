from dataclasses import dataclass

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from scripts.config import Service
from scripts.core.constants.app_constants import Secrets
from scripts.core.services.common_services import common_router
from scripts.core.services.dashboard_services import dashboard_router
from scripts.core.services.defaults import default_router
from scripts.core.services.po_service import po_service_router
from scripts.logging.logging import logger
from scripts.utils.security_utils.jwt_signature_validator import (
    EncodedPayloadSignatureMiddleware,
)
from starlette.middleware.cors import CORSMiddleware


@dataclass
class FastAPIConfig:
    title: str = "diageo_micro_services"
    version: str = "1.0.0"
    description: str = "Microservices that will be used for Diageo specific development"


app = FastAPI(**FastAPIConfig().__dict__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

try:
    if Service.verify_signature and Service.verify_signature in {"true", "True", True}:
        app.add_middleware(
            EncodedPayloadSignatureMiddleware,
            jwt_secret=Secrets.signature_key,
            jwt_algorithms=Secrets.alg,
            protect_hosts=Service.PROTECTED_HOSTS,
        )
except Exception as e:
    logger.error(f"Main.py file error : {str(e)}")

app.include_router(default_router)
app.include_router(common_router)
app.include_router(dashboard_router)
app.include_router(po_service_router)

app.mount(
    "/assets", StaticFiles(directory=f"{Service.BUILD_DIR}/assets"), name="assets"
)


@app.get("/visualization/healthcheck")
async def ping():
    return {"status": 200}
