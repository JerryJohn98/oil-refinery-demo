from scripts.core.constants.app_constants import PSQLTableNames, PSQLSchemaNames

class POQueries:
    POST_CHANGEOVER_QUERY = f"""
    {{cte_timeblock_query}}
    SELECT DISTINCT to_po AS po_value, s.end_ts,s.start_ts
    FROM {PSQLSchemaNames.diageo_bedrock}.{PSQLTableNames.oee_post_change_over} s
    JOIN time_windows w
      ON s.start_ts <= w.end_ts AND s.end_ts >= w.start_ts
      {{filter_query}}
    ORDER BY s.start_ts;
"""

    POST_MAINTENANCE_QUERY = f"""
    {{cte_timeblock_query}}
    SELECT DISTINCT process_order AS po_value, s.end_ts,s.start_ts
    FROM {PSQLSchemaNames.diageo_bedrock}.{PSQLTableNames.oee_post_maintenance} s
    JOIN time_windows w
    ON s.start_ts <= w.end_ts AND s.end_ts >= w.start_ts
    {{filter_query}}
    ORDER BY s.start_ts;
"""
