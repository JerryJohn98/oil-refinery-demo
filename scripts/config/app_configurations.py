"""
This file exposes configurations from config file and environments as Class Objects
"""

if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
import os.path
import sys
from configparser import BasicInterpolation, ConfigParser


class EnvInterpolation(BasicInterpolation):
    """
    Interpolation which expands environment variables in values.
    """

    def before_get(self, parser, section, option, value, defaults):
        value = super().before_get(parser, section, option, value, defaults)

        if not os.path.expandvars(value).startswith("$"):
            return os.path.expandvars(value)
        else:
            return


def load_config(config_path: str) -> ConfigParser:
    """
    Loads and returns the configuration from the specified path.

    Args:
        config_path (str): Path to the configuration file.

    Returns:
        ConfigParser: The loaded configuration parser.
    """
    config = ConfigParser(interpolation=EnvInterpolation())
    try:
        # print(f"Loading configuration from: {config_path}")
        config.read(config_path)
    except Exception as e:
        print(f"Error while loading the config: {e}")
        print("Failed to Load Configuration. Exiting!!!")
        sys.stdout.flush()
        sys.exit(1)
    return config


config = load_config("conf/application.conf")


class ServiceConfig:
    HOST = config.get("SERVICE", "host")
    PORT = int(config.get("SERVICE", "port"))
    WORKERS = int(config.get("SERVICE", "workers"))
    verify_signature = config.getboolean("SERVICE", "verify_signature", fallback=True)
    PROTECTED_HOSTS = config.get("SERVICE", "protected_hosts").split(",")


class Logging:
    """
    Logging settings configured from the loaded configuration and environment variables.
    """

    level = config.get("LOGGING", "level", fallback="INFO")
    level = level or "INFO"
    print(f"Logging Level set to: {level}")
    ENABLE_FILE_LOG = config.getboolean("LOGGING", "ENABLE_FILE_LOG", fallback=False)
    ENABLE_CONSOLE_LOG = config.getboolean(
        "LOGGING", "ENABLE_CONSOLE_LOG", fallback=True
    )
    LOG_ENABLE_TRACEBACK = config.getboolean(
        "SERVICE", "enable_traceback", fallback=False
    )


class Timezone:
    """
    Timezone settings configured from the loaded configuration.
    """

    desired_time_zone = config.get("TIME_ZONE", "desired_time_zone", fallback="UTC")


class Auth:
    host_name = config.get("AUTH", "host_name", fallback="localhost")


class DBConf:
    MONGO_URI = config.get("MONGO_DB", "uri_mongo")
    if not MONGO_URI:
        print("Error, environment variable MONGO_URI not set")
        sys.exit(1)
    use_postgres = config.get("POSTGRES", "use_postgres", fallback=False)
    if use_postgres:
        postgres_uri = config.get("POSTGRES", "uri")
        if not postgres_uri:
            print(
                "Environment variable POSTGRES_URI not set, proceeding without Postgres Support"
            )
            sys.exit(1)
        ASSISTANT_DB_URI = f"{postgres_uri}"
        ASSISTANT_DB = config.get("POSTGRES", "assistant_db")
        UNIFIED_MODEL_DB = config.get("POSTGRES", "unified_model")
        ILENS_EVENT_DB = config.get("POSTGRES", "ilens_event_db")
        ILENS_OEE_DB = config.get("POSTGRES", "ilens_oee_db")
        SHIFT_PLANNING_DB = config.get("POSTGRES", "shift_planning_db")
    pg_schema = config.get("POSTGRES", "pg_schema", fallback="public")
    pg_remove_prefix = config.getboolean("POSTGRES", "pg_remove_prefix", fallback=False)

    KAIROS_URI = config.get("KAIROS", "kairos_uri")
    if not KAIROS_URI:
        print("Error, environment variable KAIROS_URI not set")
        sys.exit(1)


class DatabaseConstants:
    metadata_db = config.get("DATABASES", "metadata_db")
    if not bool(metadata_db):
        metadata_db = "ilens_configuration"
    ilens_assistant_db = config.get("DATABASES", "ilens_assistant")
    if not bool(ilens_assistant_db):
        ilens_assistant_db = "ilens_assistant"
    project_126_diageo_db = config.get("DATABASES", "diageo_db")
    if not bool(project_126_diageo_db):
        project_126_diageo_db = "diageo"


class ProjectConstants:
    pagination_count = config.get("PROJECT_CONFIG", "pagination_count")


class PathToStorage:
    BASE_PATH = config.get("DIRECTORY", "base_path")
    if not BASE_PATH:
        print("Error, environment variable BASE_PATH not set")
        sys.exit(1)
    MOUNT_DIR = config.get("DIRECTORY", "mount_dir")
    if not MOUNT_DIR:
        print("Error, environment variable MOUNT_DIR not set")
        sys.exit(1)
    MODULE_PATH = os.path.join(BASE_PATH, MOUNT_DIR)
