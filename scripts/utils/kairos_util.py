import requests
from scripts.config.app_configurations import DBConf


class KairosDBUtility:
    def __init__(self):
        self.base_url = DBConf.KAIROS_URI

    def read(self, query_json):
        """
        Reads data from KairosDB.

        :param query_json: JSON object containing the query
        :return: JSON object with the data or status
        """
        url = self.base_url + "/api/v1/datapoints/query"
        return requests.post(url, json=query_json)

    def write(self, metric_json):
        """
        Writes data to KairosDB.

        :param metric_json: JSON object containing the data to be written
        :return: JSON object with the status or response
        """
        url = self.base_url + "/api/v1/datapoints"
        return requests.post(url, json=metric_json)

    def delete(self, delete_json):
        """
        Deletes data from KairosDB.

        :param delete_json: JSON object containing the deletion criteria
        :return: JSON object with the status or response
        """
        url = self.base_url + "/api/v1/datapoints/delete"
        return requests.post(url, json=delete_json)
