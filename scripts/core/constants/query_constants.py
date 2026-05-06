class ProductionPlanQuery:
    process_order_query = """SELECT process_order
                            FROM production_plan
                            WHERE scheduled_start_time AT TIME ZONE '{tz}' <= :end_time AND scheduled_end_time AT TIME ZONE '{tz}' >= :start_time
                            AND line = :line_id;"""

    production_plan_query = """
                                SELECT
                                    process_order
                                FROM public.production_plan_view
                                {filter_query}
                                ORDER BY scheduled_start_time
                                LIMIT 1
                                """

    shift_dt_interval_query = """
                                    SELECT
                                        DISTINCT ON (shift_id, start_time, end_time)
                                        shift_id,

                                        TO_CHAR(
                                            GREATEST(start_time, TIMESTAMP '{input_start_date}') AT TIME ZONE '{tz}' AT TIME ZONE 'UTC',
                                            'YYYY-MM-DD HH24:MI:SS'
                                        ) AS start_date,

                                        TO_CHAR(
                                            LEAST(end_time, TIMESTAMP '{input_end_date}') AT TIME ZONE '{tz}' AT TIME ZONE 'UTC',
                                            'YYYY-MM-DD HH24:MI:SS'
                                        ) AS end_date,

                                        (EXTRACT(EPOCH FROM GREATEST(start_time, TIMESTAMP '{input_start_date}') AT TIME ZONE '{tz}' AT TIME ZONE 'UTC') * 1000)::BIGINT AS epoch_start_time,

                                        (EXTRACT(EPOCH FROM LEAST(end_time, TIMESTAMP '{input_end_date}') AT TIME ZONE '{tz}' AT TIME ZONE 'UTC') * 1000)::BIGINT AS epoch_end_time

                                    FROM {schema}.{table_name}
                                    WHERE
                                        shift_id = '{shift_id}' AND
                                        date BETWEEN '{input_start_date}' AND '{input_end_date}'
                                    ORDER BY shift_id, start_time, end_time, date;
                                    """