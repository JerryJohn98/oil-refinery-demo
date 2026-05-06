import pathlib

from pydantic import Field
from pydantic_settings import BaseSettings
from scripts.config.app_configurations import PathToStorage, ServiceConfig


class _Service(BaseSettings):
    HOST: str = Field(default=ServiceConfig.HOST, env="service_host")
    PORT: int = Field(default=int(ServiceConfig.PORT), env="service_port")
    PROTECTED_HOSTS: str = Field(
        default=ServiceConfig.PROTECTED_HOSTS, env="PROTECTED_HOSTS"
    )
    verify_signature: bool = Field(
        default=ServiceConfig.verify_signature, env="VERIFY_SIGNATURE"
    )
    BUILD_DIR: str = Field(default="scripts/templates")
    PROXY: str = Field(default="/hack-repl")
    BACKEND_DIR: str = Field(default=".")


class _BasePathConf(BaseSettings):
    # BASE_PATH: str = "/code/data"
    BASE_PATH: str = Field(default=PathToStorage.BASE_PATH, env="BASE_MOUNT")


class _PathConf:
    BASE_PATH: pathlib.Path = pathlib.Path(_BasePathConf().BASE_PATH)


Service = _Service()
PathConf = _PathConf()
