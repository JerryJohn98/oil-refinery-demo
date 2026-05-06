import json
from datetime import datetime, timezone
from operator import itemgetter
from scripts.core.constants.query_constants import ProductionPlanQuery
import pytz
from scripts.core.constants.app_constants import CommonConstants
from scripts.core.constants.defaults import (
    DEFAULT_TIME_FORMAT_WITH_FS,
    TIME_FORMAT_YYY_MM_DD,
)
from scripts.core.constants.time_formats import AppTimeFormats
from scripts.db.mongo.ilens_configuration.aggregations.customer_projects import (
    CustomerProjectAggregate,
)
from scripts.db.mongo.ilens_configuration.collections.accessible_hierarchy import (
    AccessibleHierarchyCollection,
)
from scripts.db.mongo.ilens_configuration.collections.customer_projects import (
    CustomerProjectsCollection,
)
from scripts.db.mongo.ilens_configuration.collections.data_model_details import DataModelDetailsCollection
from scripts.db.mongo.ilens_configuration.collections.dynamic_hierarchy_details import (
    HierarchyDetailsCollection,
)
from scripts.logging.logging import logger
from scripts.utils.mongo_util import mongo_client


class CommonUtils:
    def __init__(self, project_id=None,shift_planning_db_obj=None):
        self.project_id = project_id
        self.shift_db_obj = shift_planning_db_obj
        self.hierarchy_details_instance = HierarchyDetailsCollection(
            mongo_client=mongo_client, project_id=project_id
        )
        self.accessible_hierarchy_instance = AccessibleHierarchyCollection(
            mongo_client=mongo_client
        )
        self.customer_projects_instance = CustomerProjectsCollection(
            mongo_client=mongo_client
        )
        self.data_model_details_instance = DataModelDetailsCollection(
            mongo_client=mongo_client
        )

    @staticmethod
    def load_json_from_file(file_path):
        with open(file_path) as f:
            return json.loads(f.read())

    @staticmethod
    def calc_duration_in_hhmm_format_for_ts(start_time, end_time):
        try:
            try:
                # Parse strings to datetime objects and calculate duration in seconds
                duration_seconds = (
                    datetime.strptime(end_time, TIME_FORMAT_YYY_MM_DD)
                    - datetime.strptime(start_time, TIME_FORMAT_YYY_MM_DD)
                ).total_seconds()
            except Exception:
                # Calculate the total duration in seconds
                duration_seconds = (end_time - start_time).total_seconds()

            # Check for negative duration
            if duration_seconds < 0:
                raise ValueError("End time must be after start time.")

            # Calculate hours and minutes using divmod
            hours, minutes = divmod(int(duration_seconds), 3600)
            minutes //= 60  # Convert remaining seconds to minutes

            # Conditionally format the output
            if minutes == 0:
                return f"{hours} hr"  # Only show hours if minutes are zero
            return f"{hours} hr {minutes} min"
        except Exception as e:
            logger.error(f"Failed to calculate duration: {e}")
            raise

    def fetch_hierarchy_data_by_node_id(self, node_id_list):
        try:
            query = {"node_id": {"$in": node_id_list}, "project_id": self.project_id}
            projection = {"_id": 0, "node_id": 1, "name": 1}
            data = self.hierarchy_details_instance.find_by_condition(
                query=query, projection=projection
            )
            return data
        except Exception as data_error:
            logger.error(f"Failed to fetch hierarchy data: {data_error}")
            raise data_error

    def convert_timestamp_format(
        self,
        input_date,
        current_format=DEFAULT_TIME_FORMAT_WITH_FS,
        target_format=TIME_FORMAT_YYY_MM_DD,
    ):
        try:
            if isinstance(input_date, str):
                input_date = datetime.strptime(input_date, current_format)
            return input_date.strftime(target_format)
        except Exception as conversion_error:
            logger.error(f"Failed to convert timestamp: {conversion_error}")
            raise conversion_error

    def generate_filter_query(
        self, header_filters={}, filter_model={}, foreign_table_mappings=None, tz=None
    ):
        # Generate header query
        # filter_query = [
        #     f"{key} = {value}" for key, value in header_filters.items()
        # ]

        filter_query = []
        for key, value in header_filters.items():
            # If the value is a list, use the IN operator
            if isinstance(value, list):
                formatted_values = []
                for each_val in value:
                    if isinstance(value, int):
                        formatted_values.append(str(each_val))
                    else:
                        formatted_values.append(f"'{each_val}'")

                filter_query.append(f"{key} IN ({', '.join(formatted_values)})")
            else:
                filter_query.append(f"{key} = {value}")

        # Generate query from filterModel
        filter_query += [
            self.parse_filter_condition(column, condition, foreign_table_mappings, tz)
            for column, condition in filter_model.items()
        ]

        # Generate final filter query
        final_filter_query = (
            f"WHERE {' AND '.join(filter(None, filter_query))}" if filter_query else ""
        )

        return final_filter_query.strip()

    def parse_filter_condition(
        self, column, condition, foreign_table_mappings={}, tz=None
    ):
        filter_type = condition.get("filterType")
        filter_value = condition.get("filter", "")

        # Handle nested conditions (AND/OR)
        if "operator" in condition:
            cond1 = self.parse_filter_condition(column, condition["condition1"])
            cond2 = self.parse_filter_condition(column, condition["condition2"])
            operator = condition["operator"]
            return f"({cond1} {operator} {cond2})"

        # date picker query
        if filter_type == "date":
            return self.generate_date_filter_query(
                column,
                operator=condition["type"],
                value=condition["dateFrom"],
                range_values=[condition["dateFrom"], condition["dateTo"]],
                tz=tz,
            )

        # date range query
        if isinstance(filter_value, list):
            daterange_picker_col = [0, 1]
            start_col = daterange_picker_col[0]
            end_col = daterange_picker_col[1]
            start_time = self.convert_to_timezone(filter_value[0], tz)
            if len(filter_value) == 2:
                end_time = self.convert_to_timezone(filter_value[1], tz)
                return f"DATE({start_col}) >= '{start_time}' AND DATE({end_col}) <= '{end_time}'"
            return f"DATE({start_col}) >= '{start_time}'"

        if column in foreign_table_mappings.keys():
            column = f"{foreign_table_mappings[column]}"

        # Map conditions to SQL syntax (case insensitive)
        if filter_type == "text":
            type_map = {
                "contains": f"LOWER({column}) LIKE LOWER('%{filter_value}%')",
                "notContains": f"LOWER({column}) NOT LIKE LOWER('%{filter_value}%')",
                "equals": f"LOWER({column}) = LOWER('{filter_value}')",
                "notEqual": f"LOWER({column}) != LOWER('{filter_value}')",
                "startsWith": f"LOWER({column}) LIKE LOWER('{filter_value}%')",
                "endsWith": f"LOWER({column}) LIKE LOWER('%{filter_value}')",
                "blank": f"({column} IS NULL OR {column} = '')",
                "notBlank": f"({column} IS NOT NULL AND {column} != '')",
            }
            return type_map.get(condition.get("type"), "")

        values = condition.get("values", [])
        if values:
            formatted_values = ", ".join(
                f"'{v}'" if isinstance(v, str) else f"{v}" for v in values
            )
            return f"{column} IN ({formatted_values})"

        return ""

    def generate_date_filter_query(
        self, column_name, operator, value=None, range_values=None, tz=None
    ):
        try:
            # Convert value and range values to timezone-aware format
            if value:
                value = self.convert_to_timezone(value, tz)
            if range_values:
                range_values = self.convert_range_to_timezone(range_values, tz)

            operator_mapping = {
                "equals": f"DATE({column_name}) = '{value}'",
                "greaterThan": f"DATE({column_name}) > '{value}'",
                "lessThan": f"DATE({column_name}) < '{value}'",
                "notEqual": f"DATE({column_name}) != '{value}'",
                "blank": f"DATE({column_name}) IS NULL",
                "notBlank": f"DATE({column_name}) IS NOT NULL",
            }

            if operator == "inRange" and len(range_values) == 2:
                return f"DATE({column_name}) BETWEEN '{range_values[0]}' AND '{range_values[1]}'"

            condition = operator_mapping.get(operator)
            return condition
        except Exception as filter_error:
            logger.error(f"Failed to generate date filter query: {filter_error}")
            raise filter_error

    @staticmethod
    def generate_sort_query(sort_model, foreign_table_mapping={}):
        """Generates the ORDER BY clause based on the sortModel."""
        if not sort_model:
            return ""
        sort_query = ""
        for item in sort_model:
            col = item["colId"]
            sort_order = item["sort"]
            if col in foreign_table_mapping.keys():
                col = f"{foreign_table_mapping[col]}"
            sort_query = f"ORDER BY {col} {sort_order}"
            break
        return sort_query.strip()

    @staticmethod
    def format_and_sort_dropdown_list(data_list, label_key, value_key):
        """Utility function to load and sort dropdown data."""
        return sorted(
            [
                {"label": each[label_key], "value": each[value_key]}
                for each in data_list
            ],
            key=itemgetter("label"),
        )

    @staticmethod
    def format_date_columns(
            columns,
            tz,
            time_format=AppTimeFormats.USER_META_24_HR_FORMAT,
            aggregation_mapping={},
            use_alias=True,
            time_column=None,
    ):
        """
        Helper function to format date columns.
        Automatically excludes table aliases from the alias name in the query,
        """
        time_column = f"+ {time_column}" if time_column else ""
        formatted_columns = []

        for col in columns:
            # Check if aliasing exists (contains a dot) and extract alias
            alias = col.split(".")[-1] if "." in col else col

            # Prepare the core formatted expression
            time_expr = (
                f"TO_CHAR({col} AT TIME ZONE '{tz}' {time_column}, '{time_format}')"
            )

            # Apply aggregation if necessary
            if col in aggregation_mapping:
                expr = f"{aggregation_mapping[col]}({time_expr})"
            else:
                expr = time_expr

            # Apply aliasing if needed
            if use_alias:
                formatted_columns.append(f"{expr} AS {alias}")
            else:
                formatted_columns.append(expr)

        return ", ".join(formatted_columns)

    @staticmethod
    def convert_ts_to_daterange_format(start_time, end_time):
        try:
            # Convert strings to datetime objects
            start_dt = datetime.strptime(start_time, DEFAULT_TIME_FORMAT_WITH_FS)
            end_dt = datetime.strptime(end_time, DEFAULT_TIME_FORMAT_WITH_FS)

            # Handle different years scenario
            if start_dt.year != end_dt.year:
                formatted_date_range = (
                    f"{start_dt.strftime('%b %d, %Y')} - {end_dt.strftime('%b %d, %Y')}"
                )
            else:
                formatted_date_range = (
                    f"{start_dt.strftime('%b %d')} - {end_dt.strftime('%b %d, %Y')}"
                )
            return formatted_date_range
        except Exception as conversion_error:
            logger.error(
                f"Failed to convert timestamp to date range format: {conversion_error}"
            )
            raise conversion_error

    def extract_user_access_to_hierarchy_level(self, user_id):
        try:
            query = {"user_id": user_id, "project_id": self.project_id}
            user_details = self.accessible_hierarchy_instance.find_by_condition(
                query=query, projection={"_id": 0, "access_level_list": 1}
            )
            user_details = user_details[0] if user_details else {}

            # Get hierarchy levels
            hierarchy_levels = self.data_model_details_instance.find_by_condition(
                query={"project_id": self.project_id},
                projection={"_id": 0, "level": 1, "table": 1},
            )

            # Build hierarchy level mapping
            hierarchy_level_id = {
                each["table"].lower(): each["level"] for each in hierarchy_levels
            }

            # Process access level list
            access_level = user_details.get("access_level_list", {})
            level_node_id = {key: sorted(value) for key, value in access_level.items()}

            return level_node_id, hierarchy_level_id
        except Exception as ex:
            logger.error(f"Failed to extract user access to hierarchy level: {ex}")
            raise ex

    def extract_accessible_hierarchy_node_id(self, user_id):
        try:
            level_node_id, hierarchy_level_id = (
                self.extract_user_access_to_hierarchy_level(user_id=user_id)
            )
            node_ids = ["site", "area", "line", "equipment"]
            node_id_map = {
                node: level_node_id.get(hierarchy_level_id.get(node, ""), [])
                for node in node_ids
            }
            return node_id_map, hierarchy_level_id
        except Exception as fetch_error:
            logger.error(
                f"Failed to extract user access to hierarchy level: {fetch_error}"
            )
            raise fetch_error

    def get_names_from_mongo(self, field_ids_map, project_id, name_field="name"):
        """
        Fetch names for the given field IDs from MongoDB.
        """
        try:
            names_map = {}

            for field, field_ids in field_ids_map.items():
                # Fetch names for the current field
                if field_ids:
                    plant_query = {
                        "node_id": {"$in": field_ids},  # IDs to be matched
                        "project_id": project_id,  # Ensure we are fetching for the correct project
                    }
                    projection = {"_id": 0, name_field: 1, "node_id": 1}

                    # Fetch the plant data (names) from MongoDB
                    plant_data = self.hierarchy_details_instance.find_by_condition(
                        query=plant_query, projection=projection
                    )

                    # Map the field IDs to their corresponding names
                    name_dict = {
                        plant["node_id"]: plant.get(name_field, "")
                        for plant in plant_data
                    }
                    names_map[field] = name_dict

            return names_map
        except Exception as e:
            logger.error(f"Error fetching names from MongoDB: {e}")
            raise

    def update_field_name_from_mongo(self, data, field_to_process):
        """
        Updates a single field in the given data by fetching names from MongoDB.
        """
        try:
            # Prepare the list of IDs for the field to process
            field_ids = [
                row.get(field_to_process, "")
                for row in data
                if row.get(field_to_process)
            ]

            # Fetch the names from MongoDB using the helper method
            field_ids_map = {field_to_process: field_ids}
            names_map = self.get_names_from_mongo(
                field_ids_map=field_ids_map,
                project_id=self.project_id,
                name_field="name",
            )

            # Update the data with the fetched names for the field
            updated_data = []
            for row in data:
                field_id = row.get(field_to_process, "")
                if field_id:
                    row[field_to_process] = names_map.get(field_to_process, {}).get(
                        field_id, field_id
                    )
                updated_data.append(row)

            return updated_data
        except Exception as e:
            logger.error(f"Error forming field: {e}")
            raise

    def convert_timestamp(self, timestamp):
        try:
            return (
                self.convert_timestamp_format(
                    input_date=timestamp,
                    current_format=TIME_FORMAT_YYY_MM_DD,
                    target_format=DEFAULT_TIME_FORMAT_WITH_FS,
                )
                if timestamp
                else ""
            )
        except Exception as convert_error:
            logger.error(f"Failed to convert the timestamp: {convert_error}")
            raise convert_error

    def get_formatted_schedule(
        self,
        scheduled_start_time,
        scheduled_end_time,
        input_format="%Y-%m-%d %H:%M:%S",
        output_format="%b %d, %Y",
    ):
        """
        This function formats the start and end times into the desired format.
        """

        # If the input times are string, convert them to datetime objects using the input_format
        if isinstance(scheduled_start_time, str):
            scheduled_start_time = datetime.strptime(scheduled_start_time, input_format)
        if isinstance(scheduled_end_time, str):
            scheduled_end_time = datetime.strptime(scheduled_end_time, input_format)

        # Format both start and end times
        formatted_start_time = (
            scheduled_start_time.strftime(output_format) if scheduled_start_time else ""
        )
        formatted_end_time = (
            scheduled_end_time.strftime(output_format) if scheduled_end_time else ""
        )

        # Return the formatted result
        return f"{formatted_start_time} - {formatted_end_time}"

    def add_timezone(self, date_string, timezone_name):
        """
        Adds a timezone offset to a naive date string and returns the datetime with offset.
        """
        try:
            # Basic validation of inputs
            if not date_string or not timezone_name:
                return None
            try:
                timezone = pytz.timezone(timezone_name)
            except pytz.UnknownTimeZoneError:
                return f"Error: Unknown timezone '{timezone_name}'"
            try:
                naive_datetime = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return "Error: Incorrect date format, expected 'YYYY-MM-DD HH:MM:SS'"
            aware_datetime = timezone.localize(naive_datetime)
            return aware_datetime

        except Exception as e:
            return f"Error: {str(e)}"

    def generate_global_filter_query(
        self, request_data, archive_filter=False, table_alias=None
    ):
        try:
            filters_map = CommonConstants.filter_map
            filter_query = {}

            site_id = request_data.site
            area_id = request_data.area
            line_id = request_data.line

            node_id_map = {}
            hierarchy_data = [site_id.lower(), area_id.lower(), line_id.lower()]
            if any(item in CommonConstants.default_filters for item in hierarchy_data):
                node_id_map, _ = self.extract_accessible_hierarchy_node_id(
                    user_id=request_data.user_id
                )

            # Iterate over filters_map to construct the query
            for key, value in filters_map.items():
                field_value = getattr(request_data, value, None)
                if field_value.lower() in CommonConstants.default_filters:
                    node_id_list = node_id_map[key]
                    query_key = f"{table_alias}.{key}" if table_alias else key
                    filter_query[query_key] = node_id_list
                else:
                    query_key = f"{table_alias}.{key}" if table_alias else key
                    filter_query[query_key] = f"'{field_value}'"

            if archive_filter:
                archive_key = f"{table_alias}.archive" if table_alias else "archive"
                filter_query.update({archive_key: False})

            filter_query = self.generate_filter_query(header_filters=filter_query)
            return filter_query
        except Exception as generate_error:
            logger.error(f"Failed to generate filter query: {generate_error}")
            raise generate_error

    def generate_table_body_hierarchy_filter(self, request_data, header_filters):
        try:
            site_id = request_data.site
            area_id = request_data.area
            line_id = request_data.line
            filters_map = CommonConstants.filter_map

            hierarchy_data = [site_id.lower(), area_id.lower(), line_id.lower()]
            node_id_map = {}
            if any(item in CommonConstants.default_filters for item in hierarchy_data):
                node_id_map, _ = self.extract_accessible_hierarchy_node_id(
                    user_id=request_data.user_id
                )

            # Iterate over filters_map to construct the query
            for key, value in filters_map.items():
                field_value = getattr(request_data, value, None)
                if field_value.lower() in CommonConstants.default_filters:
                    node_id_list = node_id_map[key]
                    header_filters[key] = node_id_list
                else:
                    header_filters[key] = f"'{field_value}'"
            return header_filters
        except Exception as generate_error:
            logger.error(f"Failed to generate query: {generate_error}")
            raise generate_error

    def fetch_accessible_filter_line_data(self, request_data):
        try:
            level_node_id, hierarchy_level_id = (
                self.extract_user_access_to_hierarchy_level(
                    user_id=request_data.user_id
                )
            )

            line_id_list = level_node_id.get(hierarchy_level_id.get("line", ""), [])
            query = {
                "node_id": {"$in": line_id_list},
                "project_id": request_data.project_id,
            }
            projection = {"_id": 0, "name": 1, "node_id": 1, "parent_id": 1}

            formatted_line_data = self.format_and_sort_dropdown_list(
                data_list=self.hierarchy_details_instance.find_by_condition(
                    query=query, projection=projection
                ),
                label_key="name",
                value_key="node_id",
            )
            return formatted_line_data
        except Exception as fetch_error:
            logger.error(f"Failed to fetch data: {fetch_error}")
            raise fetch_error

    @staticmethod
    def convert_to_timezone(date_value, tz):
        """
        Convert a date string to a timezone-aware ISO format, handling multiple formats.
        """
        if not date_value or not tz:
            return date_value  # Return as-is if no timezone or invalid date.
        try:
            timezone = pytz.timezone(tz)
            dt = None
            for fmt in CommonConstants.date_formats:
                try:
                    if fmt.endswith("%z"):  # Handle timezone-aware inputs directly
                        dt = datetime.strptime(date_value, fmt)
                        break
                    else:
                        dt = datetime.strptime(date_value, fmt)
                        dt = timezone.localize(dt)  # Localize to the provided timezone
                        break
                except ValueError:
                    continue

            if not dt:
                raise ValueError(f"Unrecognized date format: {date_value}")

            return dt.isoformat()
        except Exception as e:
            raise ValueError(
                f"Error in converting date '{date_value}' to timezone '{tz}': {e}"
            )

    def convert_range_to_timezone(self, range_values, tz):
        """
        Convert a range of date strings to timezone-aware ISO format.
        """
        if not range_values or len(range_values) != 2:
            return range_values  # Return as-is if not a valid range.
        try:
            return [self.convert_to_timezone(value, tz) for value in range_values]
        except Exception as e:
            raise ValueError(f"Error in converting range to timezone '{tz}': {e}")

    @staticmethod
    def update_custom_date_from_epoch(custom_date):
        try:
            custom = custom_date.get("custom")
            label_data = custom_date.get("labelData")

            if not custom or not label_data:
                raise ValueError("Missing required fields in custom_date")

            def convert_timestamp(value):
                utc_dt = datetime.fromtimestamp(value / 1000, tz=timezone.utc)
                return utc_dt.strftime("%Y-%m-%d %H:%M:%S").format(value % 1000)
            label_data.setdefault("label", {})["start"] = convert_timestamp(
                custom["from"]
            )
            label_data["label"]["end"] = convert_timestamp(custom["to"])

            return label_data
        except Exception as e:
            logger.error(f"Error updating custom date from epoch: {e}")
            return None

    @staticmethod
    def generate_equal_hierarchy_query(hierarchy_data, column="hierarchy"):
        """ """
        hierarchy = "$".join(f"{value}" for value in hierarchy_data.values())
        query = f"WHERE {column} = ('{hierarchy}')"
        return query, hierarchy

    def fetch_shift_date_range(self, start_time, end_time, shift_id,tz):
        try:
            final_query = ProductionPlanQuery.shift_dt_interval_query.format(
                schema="public",
                table_name="daily_shift_view",
                shift_id=shift_id,
                input_start_date=start_time,
                input_end_date=end_time,
                tz=tz
            )
            final_data = self.shift_db_obj.fetch_records_by_raw_query(raw_query=final_query)
            return final_data if final_data else []
        except Exception as ex:
            logger.error(f"Failed to calculate planned_time: {ex}")
            raise ex

    @staticmethod
    def generate_time_blocks_cte(time_blocks, cte_name="time_windows"):
        """
        Generates a SQL CTE from a list of time intervals.

        Args:
            time_blocks (list): List of dicts with 'start_date' and 'end_date' keys.
            cte_name (str): Name of the CTE to be used in SQL.

        Returns:
            str: SQL string for the CTE using VALUES.
        """
        try:
            values = []
            for block in time_blocks:
                start = block['start_date']
                end = block['end_date']
                values.append(f"('{start}'::timestamp, '{end}'::timestamp)")

            values_str = ",\n    ".join(values)

            return f"""WITH {cte_name}(start_ts, end_ts) AS (
                VALUES
                {values_str}
                )
                """
        except Exception as e:
            raise RuntimeError(f"Failed to build generate_time_blocks_cte: {e}")


    def extract_stime_etime(self, request_data, generate_cte_query=True):
        """
        Extracts the start and end time based on the provided request data.
        Returns:
            tuple: (start_time, end_time, default_response, success_status, time_duration,po)
        """
        time_blocks = []
        cte_query = ""
        try:
            # Determine the correct filter source (selected_hierarchy or widget_filter)
            tz = request_data.tz
            try:
                filter_data = request_data.selected_hierarchy.filterData
                time_picker = filter_data.get("timePickerValue", {})
                shift_filter = filter_data.get('shift_filter', {})
                custom_shift_time_picker = self.update_custom_date_from_epoch(
                    filter_data.get("custom_shift_filter_date", {}))
            except:
                filter_data = request_data.widget_filter
                time_picker = filter_data.timePickerValue
                shift_filter = filter_data.shift_filter
                custom_shift_time_picker = self.update_custom_date_from_epoch(
                    filter_data.custom_shift_filter_date)

            shift_id = shift_filter[0].get('value', '') if shift_filter else ''

            # Determine start_time and end_time based on available filters
            if custom_shift_time_picker:
                # start_time, end_time, time_duration = parse_custom_filter_timestamp(
                #     req_body=custom_shift_time_picker, time_zone=tz
                # )
                time_duration = custom_shift_time_picker.get("duration", "")
                start_time = custom_shift_time_picker.get("label").get("start")
                end_time = custom_shift_time_picker.get("label").get("end")
                if start_time and end_time:
                    if shift_id:
                        time_blocks = (
                            self.fetch_shift_date_range(start_time, end_time, shift_id,tz)
                            if start_time and end_time and shift_id
                            else []
                        )
                    else:
                        start_epoch = (
                                int(datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp()) * 1000
                        )
                        end_epoch = (
                                int(datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp()) * 1000
                        )
                        time_blocks = [{'start_date': start_time,
                                        'end_date': end_time,
                                        "epoch_start_time": start_epoch,
                                        "epoch_end_time": end_epoch}]


            logger.info(
                f"Timezone: {request_data.tz}   start_time: {start_time}    end_time: {end_time}"
            )

            # If filtering based on PO is enabled, extract date range based on selected PO

            if time_blocks and generate_cte_query:
                cte_query = self.generate_time_blocks_cte(time_blocks, cte_name="time_windows")
            # Return the extracted time range and success status
            return (
                time_blocks,
                cte_query
            )

        except Exception as extract_error:
            logger.error(f"Failed to extract start/end times: {extract_error}")
            return (
                time_blocks,
                cte_query
            )  # Return failure response in case of an error

    @staticmethod
    def generate_combined_hierarchy_query(hierarchy_data, column="hierarchy"):
        """ """
        hierarchy = "$".join(f"{value}" for value in hierarchy_data.values())
        query = f"WHERE {column} LIKE ('{hierarchy}%')"
        return query, hierarchy