from scripts.core.constants.app_constants import KairosConstants
from scripts.logging.logging import logger
from scripts.utils.kairos_util import KairosDBUtility


class KairosConn:
    def __init__(self):
        self.kairos_instance = KairosDBUtility()

    def find_key(self, metric_name, tag_value, start_date, end_date):
        try:
            query = {
                KairosConstants.start_absolute: start_date,
                KairosConstants.end_absolute: end_date,
                KairosConstants.metrics: [
                    {KairosConstants.name: metric_name, KairosConstants.tags: {}}
                ],
            }

            response_one = self.kairos_instance.read(query_json=query)
            data = response_one.json()
            data_one = data[KairosConstants.queries][0][KairosConstants.results][0][
                KairosConstants.tags
            ]
            global tag_key
            for key, value in data_one.items():
                for i in value:
                    if i == tag_value:
                        tag_key = key
                        tags = {tag_key: tag_value}
                        return tags
            return None
        except Exception as fetch_error:
            logger.error(f"Failed to find key: {fetch_error}")
            raise fetch_error

    # Function to send a query to KairosDB
    def query_kairosdb(self, metric_name, tags, start_date, end_date):
        try:
            query = {
                KairosConstants.start_absolute: start_date,
                KairosConstants.end_absolute: end_date,
                KairosConstants.metrics: [
                    {KairosConstants.name: metric_name, KairosConstants.tags: tags}
                ],
            }

            response_second = self.kairos_instance.read(query_json=query)
            return response_second.json()
        except Exception as fetch_error:
            logger.error(f"Failed to fetch data: {fetch_error}")

    # sample aggregator function # query can be updated as per requirement
    def aggregate_kairosdb(
        self,
        metric,
        tags,
        start,
        end,
        aggregation_type,
        sampling_unit,
        sampling_value,
        tz,
    ):
        query = {
            KairosConstants.start_absolute: start,
            KairosConstants.end_absolute: end,
            KairosConstants.metrics: [
                {
                    KairosConstants.name: metric,
                    KairosConstants.tags: tags,
                    KairosConstants.aggregators: [
                        {
                            KairosConstants.name: aggregation_type,
                            "sampling": {
                                "value": sampling_value,
                                "unit": sampling_unit,
                            },
                            "align_sampling": True,
                            "align_start_time": True,
                        }
                    ],
                }
            ],
            KairosConstants.plugins: [],
            KairosConstants.cache_time: 0,
            KairosConstants.time_zone: tz,
        }

        response = self.kairos_instance.read(query_json=query)
        return response.json()

    # sample aggregator group by function # query can be updated as per requirement
    def aggregate_kairosdb_group_by(
        self,
        metric,
        tags,
        start,
        end,
        aggregation_type,
        sampling_unit,
        sampling_value,
        group_by_tag,
    ):
        query = {
            KairosConstants.start_absolute: start,
            KairosConstants.end_absolute: end,
            KairosConstants.metrics: [
                {
                    KairosConstants.name: metric,
                    KairosConstants.tags: tags,
                    KairosConstants.group_by: [
                        {
                            KairosConstants.name: "tag",
                            KairosConstants.tags: [group_by_tag],
                        }
                    ],
                    KairosConstants.aggregators: [
                        {
                            KairosConstants.name: aggregation_type,
                            "sampling": {
                                "value": sampling_value,
                                "unit": sampling_unit,
                            },
                            "align_sampling": True,
                            "align_start_time": True,
                        }
                    ],
                }
            ],
            KairosConstants.plugins: [],
            KairosConstants.cache_time: 0,
        }
        logger.info("Hitting to Kairos DataBase with query")
        logger.info(query)
        response = self.kairos_instance.read(query_json=query)
        return response.json()

    def insert_data(self, metric_json):
        try:
            response = self.kairos_instance.write(metric_json=metric_json)
            if response.status_code not in [204, 200]:
                logger.info("Inserting data  failed")
                logger.warn(response.text)
                return False
            else:
                logger.info("data inserted successfully")
                return True
        except Exception as e:
            logger.error("Exception while inserting the data " + str(e))
            return False

    def delete_data(self, metric_json, from_time, to_time):
        try:
            request_data = {
                KairosConstants.metrics: metric_json,
                KairosConstants.cache_time: 0,
                KairosConstants.start_absolute: from_time,
                KairosConstants.end_absolute: to_time,
            }
            response = self.kairos_instance.delete(delete_json=request_data)
            if response.status_code not in [204, 200]:
                logger.info("error in deleting data")
                logger.warn(response.text)
                return False
            else:
                logger.info("data deleted successfully")
                return True
        except Exception as e:
            logger.error("Exception While deleting the data " + str(e))
            return False
