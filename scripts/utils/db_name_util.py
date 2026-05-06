from functools import lru_cache


@lru_cache()
def get_db_name(project_id: str, database: str, delimiter="__"):
    if project_id:
        # Get the prefix name from mongo or default to project_id
        return f"{project_id}{delimiter}{database}"
    return database
