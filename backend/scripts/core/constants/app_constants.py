from scripts.config.app_configurations import DatabaseConstants, ProjectConstants


class DatabaseNames:
    ilens_configuration = DatabaseConstants.metadata_db
    ilens_assistant = DatabaseConstants.ilens_assistant_db
    project_126_diageo_db = DatabaseConstants.project_126_diageo_db


class CollectionNames:
    hierarchy_details = "dynamic_hierarchy_details"
    accessible_hierarchy = "accessible_hierarchy"
    customer_projects = "customer_projects"
    data_model_details = "DataModelDetails"


class PSQLTableNames:
    production_plan = "production_plan"
    oee_post_maintenance = "oee_post_maintenance"
    oee_post_change_over = "oee_post_change_over"

class PSQLSchemaNames:
    public = "public"
    analytical = "analytical"
    diageo_bedrock = "diageo_bedrock"


class MongoQueryConstants:
    match = "$match"
    lookup = "$lookup"
    unwind = "$unwind"
    replace_root = "$replaceRoot"
    add_fields = "$addFields"


class CommonConstants:
    filter_map = {"line": "line", "area": "area", "site": "site"}
    line = "line"

    date_formats = [
        "%Y-%m-%d %H:%M:%S",  # Format with time
        "%Y-%m-%dT%H:%M:%S%z",  # ISO 8601 format with timezone
        "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO 8601 format with fractional seconds and 'Z'
        "%Y-%m-%d",  # Date only
    ]
    pagination_size = ProjectConstants.pagination_count

    default_filters = ["all"]
    default_filters_uppercase = ["All"]


class Secrets:
    LOCK_OUT_TIME_MINS = 30
    issuer = "ilens"
    alg = "HS256"
    signature_key = "kliLensKLiLensKL"


class KairosConstants:
    start_absolute = "start_absolute"
    end_absolute = "end_absolute"
    metrics = "metrics"
    name = "name"
    tags = "tags"
    plugins = "plugins"
    cache_time = "cache_time"
    time_zone = "time_zone"
    group_by = "group_by"
    aggregators = "aggregators"
    queries = "queries"
    results = "results"
