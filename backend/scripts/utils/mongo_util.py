import os
from datetime import datetime
from typing import Dict, List, Optional

import pytz
from pymongo import MongoClient
from pymongo.cursor import Cursor
from scripts.config.app_configurations import DBConf, Timezone
from scripts.logging.logging import logger
from scripts.utils.db_name_util import get_db_name

META_SOFT_DEL: bool = os.getenv("META_SOFT_DEL", True)


class MongoConnect:
    def __init__(self, uri):
        try:
            self.uri = uri
            self.client = MongoClient(self.uri, connect=False)
        except Exception as e:
            logger.exception(f"Failed to connect to MongoDB with URI {uri}: {e}")
            raise e

    def __call__(self, *args, **kwargs):
        return self.client

    def __repr__(self):
        return f"Mongo Client(uri:{self.uri}, server_info={self.client.server_info()})"


class MongoCollectionBaseClass:
    def __init__(
        self,
        mongo_client,
        database,
        collection,
        soft_delete: bool = META_SOFT_DEL,
    ):
        self.client = mongo_client
        self.database = database
        self.collection = collection
        self.__database = None
        self.soft_delete = soft_delete

    def __repr__(self):
        return f"{self.__class__.__name__}(database={self.database}, collection={self.collection})"

    @property
    def project_id(self):
        return self.project_id

    @project_id.setter
    def project_id(self, project_id):
        if self.__database is None:
            # storing original db name if None
            self.__database = self.database
        self.database = get_db_name(project_id=project_id, database=self.__database)

    def insert_one(self, data: Dict):
        """
        The function is used to inserting a document to a collection in a Mongo Database.
        :param data: Data to be inserted
        :return: Insert ID
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.insert_one(data)
            logger.qtrace(data)
            return response.inserted_id
        except Exception as e:
            logger.exception(f"Failed to insert: {e}")
            raise e

    def insert_many(self, data: List):
        """
        The function is used to inserting documents to a collection in a Mongo Database.
        :param data: List of Data to be inserted
        :return: Insert IDs
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.insert_many(data)
            logger.qtrace(data)
            return response.inserted_ids
        except Exception as e:
            logger.exception(f"Failed to insert multiple records: {e}")
            raise e

    def find(
        self,
        query: Dict,
        filter_dict: Optional[Dict] = None,
        sort=None,
        skip: Optional[int] = 0,
        limit: Optional[int] = None,
    ) -> Cursor:
        """
        The function is used to query documents from a given collection in a Mongo Database
        :param query: Query Dictionary
        :param filter_dict: Filter Dictionary
        :param sort: List of tuple with key and direction. [(key, -1), ...]
        :param skip: Skip Number
        :param limit: Limit Number
        :return: List of Documents
        """
        if sort is None:
            sort = []
        if filter_dict is None:
            filter_dict = {"_id": 0}
        database_name = self.database
        collection_name = self.collection
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            if len(sort) > 0:
                cursor = (
                    collection.find(
                        query,
                        filter_dict,
                    )
                    .sort(sort)
                    .skip(skip)
                )
            else:
                cursor = collection.find(
                    query,
                    filter_dict,
                ).skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            # logger.qtrace(f"{query}, {filter_dict}")
            return cursor
        except Exception as e:
            logger.exception(f"Failed to find records: {e}")
            raise e

    def find_one(self, query: Dict, filter_dict: Optional[Dict] = None):
        try:
            database_name = self.database
            collection_name = self.collection

            if filter_dict is None:
                filter_dict = {"_id": 0}
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.find_one(query, filter_dict)
            # logger.qtrace(f"{self.collection}, {query}, {filter_dict}")
            return response
        except Exception as e:
            logger.exception(f"Failed to find record: {e}")
            raise e

    def find_with_count(
        self,
        query: Dict,
        filter_dict: Optional[Dict] = None,
        sort=None,
        skip: Optional[int] = 0,
        limit: Optional[int] = None,
    ):
        """
        The function is used to query documents from a given collection in a Mongo Database
        :param query: Query Dictionary
        :param filter_dict: Filter Dictionary
        :param sort: List of tuple with key and direction. [(key, -1), ...]
        :param skip: Skip Number
        :param limit: Limit Number
        :return: List of Documents
        """
        if sort is None:
            sort = []
        if filter_dict is None:
            filter_dict = {"_id": 0}
        database_name = self.database
        collection_name = self.collection

        try:
            db = self.client[database_name]
            collection = db[collection_name]

            total_count = collection.count_documents(query)

            if len(sort) > 0:
                cursor = (
                    collection.find(
                        query,
                        filter_dict,
                    )
                    .sort(sort)
                    .skip(skip)
                )
            else:
                cursor = collection.find(
                    query,
                    filter_dict,
                ).skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            # logger.qtrace(f"{query}, {filter_dict}")
            return cursor, total_count
        except Exception as e:
            logger.exception(f"Failed to find record with count: {e}")
            raise e

    def update_one(self, query: Dict, data: Dict, upsert: bool = False):
        """

        :param upsert:
        :param query:
        :param data:
        :return:
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.update_one(query, {"$set": data}, upsert=upsert)
            # logger.qtrace(f"{self.collection}, {query}, {data}")
            return response.modified_count
        except Exception as e:
            logger.exception(f"Failed to update record: {e}")
            raise e

    def update_to_set(self, query: Dict, param: str, data: Dict, upsert: bool = False):
        """

        :param upsert:
        :param query:
        :param param:
        :param data:
        :return:
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.update_one(
                query, {"$addToSet": {param: data}}, upsert=upsert
            )
            # logger.qtrace(f"{self.collection}, {query}, {data}")
            return response.modified_count
        except Exception as e:
            logger.exception(f"Failed to update record: {e}")
            raise e

    def update_many(self, query: Dict, data: Dict, upsert: bool = False):
        """

        :param upsert:
        :param query:
        :param data:
        :return:
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.update_many(
                filter=query, update={"$set": data}, upsert=upsert
            )
            # logger.qtrace(f"{query}, {data}")
            return response.modified_count
        except Exception as e:
            logger.exception(f"Failed to update multiple records: {e}")
            raise e

    def delete_many(self, query: Dict):
        """
        :param query:
        :return:
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            if self.soft_delete:
                soft_del_query = [
                    {"$match": query},
                    {
                        "$addFields": {
                            "deleted": {
                                "on": datetime.now(
                                    pytz.timezone(Timezone.desired_time_zone)
                                )
                            }
                        }
                    },
                    {
                        "$merge": {
                            "into": {
                                "db": f"deleted__{database_name}",
                                "coll": collection_name,
                            },
                        }
                    },
                ]
                collection.aggregate(soft_del_query)
            response = collection.delete_many(query)
            # logger.qtrace(query)
            return response.deleted_count
        except Exception as e:
            logger.exception(f"Failed to delete multiple records: {e}")
            raise e

    def delete_one(self, query: Dict):
        """
        :param query:
        :return:
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.delete_one(query)
            if self.soft_delete:
                soft_del_query = [
                    {"$match": query},
                    {
                        "$addFields": {
                            "deleted": {
                                "on": datetime.now(
                                    pytz.timezone(Timezone.desired_time_zone)
                                )
                            }
                        }
                    },
                    {
                        "$merge": {
                            "into": {
                                "db": f"deleted__{database_name}",
                                "coll": collection_name,
                            },
                        }
                    },
                ]
                collection.aggregate(soft_del_query)

            # logger.qtrace(query)
            return response.deleted_count
        except Exception as e:
            logger.exception(f"Failed to delete record: {e}")
            raise e

    def distinct(self, query_key: str, filter_json: Optional[Dict] = None):
        """
        :param query_key:
        :param filter_json:
        :return:
        """
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.distinct(query_key, filter_json)
            # logger.qtrace(f"{query_key}, {filter_json}")
            return response
        except Exception as e:
            logger.exception(f"Failed to find distinct record: {e}")
            raise e

    def aggregate(
        self,
        pipelines: List,
    ):
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.aggregate(pipelines)
            # logger.qtrace(f"{self.collection}, {pipelines}")
            return response
        except Exception as e:
            logger.exception(f"Failed to find aggregate records: {e}")
            raise e

    def upsert_document(self, query_condition, records_to_insert):
        try:
            database_name = self.database
            collection_name = self.collection
            db = self.client[database_name]
            collection = db[collection_name]
            update = {"$set": records_to_insert}
            result = collection.update_one(query_condition, update, upsert=True)
            return result.modified_count
        except Exception as e:
            logger.exception(f"Failed to upsert record: {e}")
            raise e

    def fetch_records_from_object(self, body):
        """
        :param body:
        :return:
        """
        final_list = []
        try:
            for each in body:
                final_list.append(each)
        except Exception as e:
            status_message = "could not fetch records from object", str(e)
            logger.exception(status_message)
            raise e
        return final_list


class MongoAggregateBaseClass:
    def __init__(
        self,
        mongo_client,
        database,
    ):
        self.client = mongo_client
        self.database = database

    def aggregate(
        self,
        collection,
        pipelines: List,
    ):
        try:
            database_name = self.database
            collection_name = collection
            db = self.client[database_name]
            collection = db[collection_name]
            response = collection.aggregate(pipelines)
            # logger.qtrace(f"{collection}, {pipelines}")
            return response
        except Exception as e:
            logger.exception(f"Failed to find aggregate records: {e}")
            raise e


mongo_client = MongoConnect(uri=DBConf.MONGO_URI)()
