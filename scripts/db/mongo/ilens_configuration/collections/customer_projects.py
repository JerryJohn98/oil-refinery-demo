from scripts.core.constants.app_constants import CollectionNames, DatabaseNames
from scripts.utils.mongo_util import MongoCollectionBaseClass


class CustomerProjectsCollection(MongoCollectionBaseClass):
    def __init__(self, mongo_client, project_id=None):
        super().__init__(
            mongo_client,
            database=DatabaseNames.ilens_configuration,
            collection=CollectionNames.customer_projects,
        )
        self.project_id = project_id

    def find_by_aggregate(self, pipeline=None):
        try:
            record = self.aggregate(pipeline)
            record = self.fetch_records_from_object(record)
            return record
        except Exception:
            return None
